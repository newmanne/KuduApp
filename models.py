from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from django.contrib.postgres.fields import ArrayField, JSONField

'''
Models defining Application Business logic
'''


def audit_log(msg):
    if msg is not None:
        with open(settings.LOG_AUDIT, 'a') as audit_file:
            audit_file.write(msg + '\n')


class Language(models.Model):
    language = models.TextField()
    active = models.BooleanField(default=True)


class Verification(models.Model):
    code = models.TextField()
    user = models.OneToOneField(User)
    is_used = models.BooleanField(default=False)
    verified_on = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.code

    def is_expired(self):
        return self.expiry_date < now()


class UnitsDefinition(models.Model):
    '''
    Units definition
    '''
    code = models.TextField('unit', unique=True, null=False)
    unit_name = models.TextField(unique=True, null=False)

    class Meta:
        verbose_name_plural = "Units Description"

    def __str__(self):
        return self.code


class ProduceDefinition(models.Model):
    '''
    Produce description
    '''
    produce_name = models.TextField('Produce name', max_length=50, unique=False, null=True, blank=True)
    unit = models.ForeignKey(UnitsDefinition, null=False)
    display_name = models.TextField(blank=True)
    active = models.BooleanField()  # Used to turn off trading a crop on Kudu
    conversion_factor = models.FloatField(default=1, verbose_name="Conversion from units to kgs")
    image_path = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Produce Description"

    def __str__(self):
        return self.display_name


class ProduceGroup(models.Model):
    name = models.TextField()
    produce = models.ManyToManyField(ProduceDefinition)


class UserProfile(models.Model):
    '''
    Custom user profile for the admin interface
    '''
    firebase = models.CharField(max_length=150, unique=True, null=True, error_messages={
        'unique': _("A user with that firebase credential already exists."),
    })
    phone_number = PhoneNumberField(unique=True, null=True)
    user = models.OneToOneField(User, unique=True)
    primary_location = models.PointField(srid=4326, null=True)
    comments = models.TextField(blank=True)
    language = models.TextField(choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)  # Used for backend transaltions, etc.
    spoken_languages = models.ManyToManyField(Language, blank=True)

    def __str__(self):
        return "{phone_number} ({name})".format(phone_number=self.phone_number, name=self.user.get_full_name())

    def get_active_asks(self):
        return FarmerAsks.objects.filter(owner=self, active=True)


MEDIUM_WEB = 'Web'
MEDIUM_CALL_CENTER = 'CC'
MEDIUM_SMS = 'SMS'
MEDIUM_CHOICES = (
    (MEDIUM_WEB, 'Web'),
    (MEDIUM_CALL_CENTER, 'Call Center'),
    (MEDIUM_SMS, 'SMS')
)


class BidTag(models.Model):
    tag = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.tag


class AbstractBid(models.Model):
    owner = models.ForeignKey(UserProfile)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    medium = models.TextField(choices=MEDIUM_CHOICES, editable=False)
    produce = models.ForeignKey(ProduceDefinition)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    tags = models.ManyToManyField(BidTag, blank=True)

    active = models.BooleanField(default=True)
    new = models.BooleanField(default=True)
    valid = models.BooleanField(default=True)

    initial_price = models.PositiveIntegerField(null=True, editable=False)
    initial_quantity = models.PositiveIntegerField(null=True, editable=False)

    location = models.PointField(srid=4326, null=True)
    address = JSONField()
    contact_number = models.TextField()

    class Meta:
        abstract = True

    def _update_fields_for_log(self):
        for field in self.__important_fields:
            setattr(self, '__original_%s' % field, getattr(self, field))

    def __init__(self, *args, **kwargs):
        super(AbstractBid, self).__init__(*args, **kwargs)
        self.__important_fields = ['price', 'quantity']
        self._update_fields_for_log()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.initial_price = self.price
            self.initial_quantity = self.quantity
        else:
            for field in self.__important_fields:
                orig = '__original_%s' % field
                orig_val = getattr(self, orig)
                cur_val = getattr(self, field)
                if orig_val != cur_val:
                    audit_log("%s --- %s %d changed %s from %s to %s" % (
                        now(), "Ask" if isinstance(self, FarmerAsks) else "Bid", self.pk, field, orig_val, cur_val))
        super(AbstractBid, self).save(*args, **kwargs)
        self._update_fields_for_log()

    def __str__(self):
        return "ID: {id} User: {user}, Quantity: {quantity}, Price: {price}, Produce: {produce}".format(id=self.pk,
                                                                                                        user=self.owner,
                                                                                                        quantity=self.quantity,
                                                                                                        price=self.price,
                                                                                                        produce=self.produce)

    @property
    def total_price(self):
        return self.quantity * self.price

    @property
    def get_admin_url(self):
        return reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name), args=(self.id,))


def ask_expiry_default():
    return now() + FarmerAsks.EXPIRY_ASK


class PaymentMethod(models.Model):
    name = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class FarmerAsks(AbstractBid):
    EXPIRY_ASK = timedelta(days=3)

    '''
    Farmer asks that are submitted to the market
    '''
    available_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateTimeField(default=ask_expiry_default)

    view_count = models.PositiveIntegerField(default=0)

    payment_methods = models.ManyToManyField(PaymentMethod, blank=True)

    DELIVERY_YES = 'Y'
    DELIVERY_NO = 'N'
    DELIVERY_CHOICES = (
        (DELIVERY_YES, 'Yes'),
        (DELIVERY_NO, 'No'),
    )

    delivery = models.CharField(max_length=1, choices=DELIVERY_CHOICES, default=DELIVERY_NO)

    @classmethod
    def expired_q(cls):
        return Q(expiry_date__lt=now())

    class Meta:
        verbose_name_plural = "Asks"


EXPIRY_BID = timedelta(days=7)


def bid_expiry_default():
    return now() + EXPIRY_BID


class TraderBids(AbstractBid):
    '''
    Trader bids submitted to the market
    '''

    expiry_date = models.DateTimeField(default=bid_expiry_default)

    class Meta:
        verbose_name_plural = 'Bids'

    @classmethod
    def expired_q(cls):
        return Q(expiry_date__lt=now())


class FavoriteAsk(models.Model):
    user = models.ForeignKey(UserProfile)
    ask = models.ForeignKey(FarmerAsks)
    is_favorite = models.BooleanField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'ask',)


class SavedSearch(models.Model):
    owner = models.ForeignKey(UserProfile)
    produce = models.ManyToManyField(ProduceDefinition)

    # Price filters
    min_price = models.IntegerField(null=True, blank=True)
    max_price = models.IntegerField(null=True, blank=True)

    # Quantity filters
    min_quantity = models.IntegerField(null=True, blank=True)
    max_quantity = models.IntegerField(null=True, blank=True)

    # Geo filters
    sw_latlng = models.PointField(srid=4326, null=True)
    ne_latlng = models.PointField(srid=4326, null=True)

    max_age = models.IntegerField(null=True, blank=True)
    time = models.FloatField(null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    last_seen_date = models.DateTimeField(default=now)
    active = models.BooleanField(default=True)

    SEARCH_NOTIFIED = '1'
    SEARCH_TO_NOTIFY = '2'
    SEARCH_CHOICES = (
        (SEARCH_NOTIFIED, 'Notified'),
        (SEARCH_TO_NOTIFY, 'To notify'),
    )

    state = models.CharField(max_length=1, choices=SEARCH_CHOICES, default=SEARCH_NOTIFIED)

    def __str__(self):
        return f'{self.owner} {self.pk}'

    class Meta:
        verbose_name_plural = 'Saved Searches'


STATUS_REVIEWED = 'Rev'
STATUS_UNSEEN = 'Uns'
MESSAGE_STATUS = (
    (STATUS_REVIEWED, 'Reviewed'),
    (STATUS_UNSEEN, 'Unseen')
)


class UserSubmission(models.Model):
    owner = models.ForeignKey(UserProfile)
    message = models.TextField(blank=True, help_text="The incoming SMS")
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.TextField(choices=MESSAGE_STATUS, default=STATUS_UNSEEN)

    def __str__(self):
        return self.message
