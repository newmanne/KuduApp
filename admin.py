'''
Created on Mar 1, 2012
@author: rkayondo

Interface to register application components 
'''
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserProfile, ProduceDefinition, UnitsDefinition, FarmerAsks, SavedSearch, FavoriteAsk, BidTag, \
    PaymentMethod, UserSubmission, ProduceGroup


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class CustomUserAdmin(UserAdmin):
    '''
    Custom user profile with additional information
    '''
    inlines = [UserProfileInline]
    list_display = (
        'username',
        'first_name',
        'last_name',
        'comments',
        'date_joined',
        'location',
    )
    search_fields = ['first_name', 'last_name', 'userprofile__phone_number']
    list_filter = ('groups__name',)

    date_hierarchy = 'date_joined'
    ordering = ('-date_joined',)

    def comments(self, obj):
        return obj.userprofile.comments

    def location(self, obj):
        try:
            return obj.userprofile.primary_location
        except UserProfile.DoesNotExist:
            pass


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UnitsDefinition)
class UnitsDefinitionAdmin(admin.ModelAdmin):
    pass


@admin.register(ProduceDefinition)
class ProduceDefinitionAdmin(admin.ModelAdmin):
    '''
    Produce description
    '''
    list_display = ['display_name', 'produce_name', 'unit', 'conversion_factor', 'pk']
    search_fields = ['display_name', 'produce_name']


@admin.register(ProduceGroup)
class ProduceGroupAdmin(admin.ModelAdmin):
    pass


class AsksAdmin(admin.ModelAdmin):
    readonly_fields = ('initial_price', 'initial_quantity', 'medium', 'owner')
    list_display = ['ask_ID', 'created_date', 'produce', 'name', 'owner', 'quantity', 'price', 'active', 'valid']

    list_filter = ('created_date', 'produce')
    search_fields = ['id', 'owner__phone_number', 'owner__user__last_name', 'owner__user__first_name']

    def name(self, obj):
        return obj.owner.user.get_full_name()

    def ask_ID(self, obj):
        return "%s" % obj.id


admin.site.register(FarmerAsks, AsksAdmin)

@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    raw_id_fields = ('owner',)


@admin.register(FavoriteAsk)
class FavoriteAskAdmin(admin.ModelAdmin):
    list_display = ('user', 'ask', 'is_favorite')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)
    list_display = ['phone_number', 'firebase']
    search_fields = ['phone_number', 'firebase']

@admin.register(BidTag)
class BidTagAdmin(admin.ModelAdmin):
    pass

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass

@admin.register(UserSubmission)
class UserSubmissionAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date',)
    raw_id_fields = ('owner',)
