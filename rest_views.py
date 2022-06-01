import json
import logging

import rest_framework_filters as filters
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.cache import cache
from django.db import transaction, IntegrityError
from django.db.models import F, Count
from django.utils import formats, translation
from django.utils.crypto import get_random_string
from push_notifications.models import GCMDevice
from rest_framework import filters as rest_filters
from rest_framework import serializers, viewsets
from rest_framework import status
from rest_framework.decorators import permission_classes, action, api_view, authentication_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_filters.backends import RestFrameworkFilterBackend
from rest_framework_gis.filters import InBBoxFilter

from agrotrade import seller
from agrotrade.firebase_auth.authentication import get_uid
from agrotrade.i18n import _
from agrotrade.seller import make_ask
from agrotrade.buyer import make_bid
from agrotrade.sms import send_sms
from agrotrade.sms_market import detect_language
from .models import *
from rest_framework.permissions import IsAdminUser
from django.conf import settings

logger = logging.getLogger(__name__)


class ApplicationProduceSerializer(serializers.ModelSerializer):
    units = serializers.CharField(source='unit.code')

    class Meta:
        model = ProduceDefinition
        fields = ['pk', 'display_name', 'units']


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return '{} {}'.format(obj.user.first_name, obj.user.last_name)

    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone_number']


class BidTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidTag
        fields = ['pk', 'tag']


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['pk', 'name']


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 10000


class ApplicationFarmerAsksSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    produce = ApplicationProduceSerializer()
    travel_time = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    favorited_date = serializers.SerializerMethodField()
    tags = BidTagSerializer(many=True, read_only=True)
    payment_methods = PaymentMethodSerializer(many=True, read_only=True)

    def get_travel_time(self, obj):
        return 2.1

    def get_is_favorite(self, obj):
        u = self.context['request'].user
        if not u.is_authenticated():
            return False
        user = u.userprofile
        try:
            favorite_ask = FavoriteAsk.objects.get(ask=obj, user=user)
            return favorite_ask.is_favorite
        except FavoriteAsk.DoesNotExist:
            return False

    def get_favorited_date(self, obj):
        u = self.context['request'].user
        if not u.is_authenticated():
            return None
        user = u.userprofile
        try:
            favorite_ask = FavoriteAsk.objects.get(ask=obj, user=user)
            return favorite_ask.updated_date
        except FavoriteAsk.DoesNotExist:
            return None

    class Meta:
        model = FarmerAsks
        fields = ['pk', 'price', 'quantity', 'created_date', 'produce', 'owner', 'view_count', 'location',
                  'travel_time', 'tags', 'payment_methods', 'delivery', 'address', 'is_favorite', 'favorited_date',
                  'contact_number']


class PatchFarmerAsksSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerAsks
        fields = ['price', 'quantity', 'produce', 'location', 'tags', 'payment_methods', 'delivery', 'address',
                  'contact_number']


class ApplicationAskFilter(filters.FilterSet):
    price = filters.AutoFilter(lookups='__all__')
    quantity = filters.AutoFilter(lookups='__all__')
    created_date = filters.AutoFilter(lookups='__all__')
    id = filters.AutoFilter(lookups='__all__')
    produce = filters.AutoFilter(lookups='__all__')

    class Meta:
        model = FarmerAsks
        fields = []


@permission_classes((AllowAny,))
class ApplicationFarmerAsksViewSet(viewsets.ReadOnlyModelViewSet):
    # Distinct is needed here or you get duplicates when combined with pagination.
    queryset = FarmerAsks.objects.select_related('owner__user', 'produce').filter(active=True).order_by(
        '-created_date').distinct()
    serializer_class = ApplicationFarmerAsksSerializer
    ordering_fields = ('price', 'quantity',)
    filter_class = ApplicationAskFilter
    filter_backends = (InBBoxFilter, RestFrameworkFilterBackend, rest_filters.OrderingFilter)
    bbox_filter_field = 'location'
    pagination_class = LargeResultsSetPagination

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if cache.add('views:ask:{ask_id}:user:{user_id}'.format(
                ask_id=instance.pk, user_id=request.user.pk), True,
                timeout=3600):
            # Update view count
            instance.view_count = F('view_count') + 1
            instance.save()
            instance.refresh_from_db()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProduceSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = ProduceDefinition
        fields = ['pk', 'display_name', 'image_path']


class SavedSearchGetSerializer(serializers.ModelSerializer):
    produce = ProduceSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    def get_price(self, obj):
        return {
            'max': obj.max_price,
            'min': obj.min_price
        }

    def get_quantity(self, obj):
        return {
            'max': obj.max_quantity,
            'min': obj.min_quantity
        }

    class Meta:
        model = SavedSearch
        fields = ['pk', 'produce', 'time', 'state',
                  'price', 'quantity', 'max_age', 'sw_latlng', 'ne_latlng']


class SavedSearchPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = ['owner', 'produce', 'min_price', 'max_price', 'time', 'state',
                  'min_quantity', 'max_quantity', 'max_age', 'sw_latlng', 'ne_latlng']


class SavedSearchViewSet(viewsets.ModelViewSet):
    ordering_fields = ('created_date', 'state')
    serializer_class = SavedSearchGetSerializer

    def get_queryset(self):
        return SavedSearch.objects.filter(owner=self.request.user.userprofile, active=True).order_by('-created_date')

    def create(self, request, *args, **kwargs):
        request.data['owner'] = request.user.userprofile.pk
        serializer = SavedSearchPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True, url_path='delete', url_name='delete')
    def deactivate(self, request, pk=None):
        search = self.get_object()
        search.active = False
        search.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['patch'], detail=True, url_path='change-state', url_name='change_state')
    def set_state_to_notified(self, request, pk=None):
        search = self.get_object()
        search.state = SavedSearch.SEARCH_NOTIFIED
        search.last_seen_date = now()
        search.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteAskSerializer(serializers.ModelSerializer):
    ask = ApplicationFarmerAsksSerializer(read_only=True)
    favorited_date = serializers.SerializerMethodField()

    def get_favorited_date(self, obj):
        return obj.updated_date

    class Meta:
        model = FavoriteAsk
        fields = ['ask', 'favorited_date']


class FavoriteAskViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteAskSerializer
    # TODO: If more than this, results will be hidden and the user given no warning. Better to have a smaller page size and infinite scroll, but this is easier for now.
    page_size = 100

    def get_queryset(self):
        return FavoriteAsk.objects.filter(user=self.request.user.userprofile, is_favorite=True)


class UserProfileGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'primary_location', 'language']


class UserGetSerializer(serializers.ModelSerializer):
    userprofile = UserProfileGetSerializer()

    class Meta:
        model = User
        fields = ['pk', 'first_name', 'last_name', 'userprofile', 'is_staff']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['primary_location', 'language']


class UserPatchSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['pk', 'first_name', 'last_name', 'userprofile']

    def update(self, instance, validated_data):
        userprofile_data = validated_data.pop('userprofile')
        userprofile = instance.userprofile

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        userprofile.primary_location = userprofile_data.get('primary_location', userprofile.primary_location)
        userprofile.language = userprofile_data.get('language', userprofile.language)
        userprofile.save()

        return instance


@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes((AllowAny,))
def get_or_create_user(request):
    id_token = request.META.get('HTTP_AUTHORIZATION')
    if id_token is None:
        raise ValueError("ID token is None!")

    firebase = get_uid(id_token)
    if firebase is None:
        raise ValueError("Couldn't find a corresponding user for id token in firebase")

    with transaction.atomic():
        user, created = User.objects.get_or_create(
            username=request.GET.get('username', firebase)
        )
        if created:
            UserProfile.objects.create(
                firebase=firebase,
                user=user
            )
            logger.info("New user created")

    serializer = UserGetSerializer(user)
    return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserGetSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    @action(detail=False)
    def get_user(self, request):
        user = request.user
        serializer = UserGetSerializer(user)
        return Response(serializer.data)

    @action(detail=False)
    def check_valid(self, request):
        user = request.user

        name_or_location_missing = user.first_name is None \
                                   or user.last_name is None \
                                   or user.userprofile.primary_location is None

        return Response({'name_or_location_missing': name_or_location_missing,
                         'number_missing': user.userprofile.phone_number is None})

    def patch(self, request, format=None):
        user = request.user
        serializer = UserPatchSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def send_code(self, request, pk=None):
        posted_data = json.loads(request.body.decode("utf-8"))

        phone_number = posted_data['phone_number']
        try:
            u = UserProfile.objects.get(phone_number=phone_number)
            if u.user == request.user:
                return Response("No change from the already registered phone number",
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    "An account with this phone number is already registered. Cannot register a duplicate phone number.",
                    status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            pass

        user = request.user

        verification, created = Verification.objects.get_or_create(
            user=user,
            defaults={
                'code': get_random_string(length=6, allowed_chars='1234567890'),
                'expiry_date': now() + timedelta(minutes=10),
            },
        )

        if not created and verification.is_expired():
            # Issue a new code
            verification.code = get_random_string(length=6, allowed_chars='1234567890')
            verification.is_used = False
            verification.verified_on = None
            verification.expiry_date = now() + timedelta(minutes=10)
            verification.save()

        if settings.DEBUG:
            verification.code = '123456'
            verification.save()

        # TODO: A malicious or stupid user could spam this and cost you a lot money
        send_sms(f'Your verification code for Kudu is {verification.code}', phone_number)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def update_phone_number(self, request, pk=None):

        user = request.user
        verification = Verification.objects.get(user=user)

        if verification.is_expired():
            return Response("Code expired", status=status.HTTP_400_BAD_REQUEST)

        if str(request.data['code']) != verification.code:
            return Response("Code invalid", status=status.HTTP_400_BAD_REQUEST)

        user.userprofile.phone_number = request.data['phone_number']
        verification.is_used = True
        verification.verified_on = now()

        with transaction.atomic():
            user.userprofile.save()
            verification.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def update_language(self, request, pk=None):
        user = request.user
        user.userprofile.language = request.data['language']
        user.userprofile.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True)
    def register_device(self, request, pk=None):
        # Create a FCM device
        registration_id = request.GET['registration_id']
        GCMDevice.objects.get_or_create(registration_id=registration_id, cloud_message_type="FCM",
                                        user=request.user, )
        # application_id = '1066453779820'
        return Response(status=status.HTTP_204_NO_CONTENT)


class FarmerAsksSerializer(serializers.ModelSerializer):

    def save(self, request):
        return seller.make_ask(request.user.userprofile, self.validated_data['produce'],
                               self.validated_data['quantity'],
                               self.validated_data['price'], self.validated_data.get('delivery', 'N'),
                               self.validated_data.get('payment_methods', []), self.validated_data['location'],
                               tags=self.validated_data.get('tags', []),
                               contact_number=self.validated_data['contact_number'],
                               medium=MEDIUM_WEB)

    class Meta:
        model = FarmerAsks
        fields = ['pk', 'produce', 'quantity', 'price', 'payment_methods', 'delivery', 'location', 'tags',
                  'contact_number']


class MyListingsViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return FarmerAsks.objects.filter(owner=self.request.user.userprofile, active=True)

    def get_serializer_class(self):
        # Use a separate serializer here because we don't want to expand produce into a dictionary etc.
        # TODO: This won't update the text address
        if self.request.method == 'PATCH':
            return PatchFarmerAsksSerializer
        return ApplicationFarmerAsksSerializer

    def create(self, request, *args, **kwargs):
        serializer = FarmerAsksSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True, url_path='delete')
    def deactivate(self, request, pk=None):
        ask = self.get_object()
        ask.active = False
        ask.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListingsViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationFarmerAsksSerializer
    queryset = FarmerAsks.objects.all()

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        userprofile = request.user.userprofile
        ask = self.get_object()
        favorite_ask, created = FavoriteAsk.objects.get_or_create(
            user=userprofile,
            ask=ask,
            defaults={
                'is_favorite': True,
            },
        )

        if not created:
            favorite_ask.is_favorite = not favorite_ask.is_favorite
            favorite_ask.save()

        serializer = self.get_serializer(favorite_ask.ask)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecentSerializer(serializers.ModelSerializer):
    produce_name = serializers.CharField()
    produce_units = serializers.CharField()
    first_name = serializers.CharField()

    def to_representation(self, instance):
        ret = super(RecentSerializer, self).to_representation(instance)
        ret['action'] = self.get_action()
        ret['lat'] = instance.location.x
        ret['lng'] = instance.location.y
        # TODO: Really a UI concern that would be better handled in JS or with different fieldnames e.g. quantity_display
        ret['quantity'] = intcomma(ret['quantity'])
        ret['price'] = intcomma(ret['price'])
        if not ret['first_name']:
            ret['first_name'] = '(Unknown Name)'
        return ret

    class Meta:
        fields = ['produce_name', 'price', 'quantity', 'created_date', 'produce_units', 'first_name', 'created_date']


class RecentAsksSerializer(RecentSerializer):
    def get_action(self):
        return 'selling'

    class Meta(RecentSerializer.Meta):
        model = FarmerAsks


class RecentBidsPagination(PageNumberPagination):
    page_size = 35


@permission_classes((AllowAny,))
class RecentAsksViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FarmerAsks.objects.filter(active=True, valid=True, location__isnull=False).annotate(
        produce_name=F('produce__display_name'), produce_units=F('produce__unit__unit_name'),
        first_name=F('owner__user__first_name')).order_by('-created_date')
    serializer_class = RecentAsksSerializer
    pagination_class = RecentBidsPagination


class AsksSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerAsks
        fields = ['pk', 'price', 'quantity', 'created_date', 'medium']


@permission_classes((AllowAny,))
class ProduceViewSet(viewsets.ReadOnlyModelViewSet):
    # TODO: May want to reoorder by past month count or something
    queryset = ProduceDefinition.objects.filter(active=True).annotate(count=Count('farmerasks')).order_by('-count')
    serializer_class = ProduceSerializer
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BidTag.objects.filter(active=True)
    serializer_class = BidTagSerializer
    pagination_class = None


class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentMethod.objects.filter(active=True)
    serializer_class = PaymentMethodSerializer
    pagination_class = None


class SMSFilter(filters.FilterSet):
    status = filters.AutoFilter(lookups='__all__')
    id = filters.AutoFilter(lookups='__all__')

    class Meta:
        model = UserSubmission
        fields = []


class SMSSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = UserSubmission
        fields = ['pk', 'message', 'created_date', 'owner']


@permission_classes((IsAdminUser,))
class SMSViewSet(viewsets.ModelViewSet):
    queryset = UserSubmission.objects.all().order_by('-created_date')
    serializer_class = SMSSerializer
    filter_class = SMSFilter
    pagination_class = LargeResultsSetPagination

    @action(detail=False, methods=['post'])
    def send_message(self, request):
        content = request.data.get('content')
        number = request.data.get('number')
        send_sms(content, number)
        return Response({'status': 'ok', 'reply': content})

    @action(detail=True, methods=['post'])
    def correct_message(self, request, pk=None):
        message = self.get_object()

        userprofile = message.owner
        intent = request.data.get('intent')
        # TODO: May want to pass this through a form...
        produce = ProduceDefinition.objects.get(pk=request.data.get('produce'))
        quantity = int(request.data.get('quantity'))
        price = int(request.data.get('price'))

        if intent == 'Sell':
            make_ask(userprofile, produce, quantity, price,
                     'N', [],
                     None,  # TODO: LOCATION
                     tags=[],
                     contact_number=userprofile.phone_number,
                     medium=MEDIUM_SMS)
            with translation.override(detect_language(message.message, userprofile=userprofile)):
                response = (_('Thanks for your submission to Kudu. We will contact you shortly if more details are required.'))
                send_sms(response, userprofile.phone_number)
        elif intent == 'Buy':
            # TODO:
            make_bid(userprofile, produce, quantity, price, location=None,
                     contact_number=userprofile.phone_number,
                     medium=MEDIUM_SMS)
            with translation.override(detect_language(message.message, userprofile=userprofile)):
                response = (_('Thanks for your submission to Kudu. We will contact you shortly if more details are required.'))
                send_sms(response, userprofile.phone_number)
        else:
            raise ValueError("Unrecognized intent")

        message.status = STATUS_REVIEWED
        message.save()
        return Response({'status': 'ok', 'reply': response})
