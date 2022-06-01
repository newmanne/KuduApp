from django.conf.urls import include, url  # , handler404, handler500
# import django.conf.urls.handler404
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from rest_framework import routers

from agrotrade import rest_views
from agrotrade import views
from push_notifications.api.rest_framework import GCMDeviceAuthorizedViewSet


# from django.views.generic.simple import direct_to_template

router = routers.DefaultRouter()
router.register(r'produce', rest_views.ProduceViewSet)
router.register(r'tags', rest_views.TagViewSet)
router.register(r'payment_methods', rest_views.PaymentMethodViewSet)
router.register(r'recent_asks', rest_views.RecentAsksViewSet)
router.register(r'application_asks', rest_views.ApplicationFarmerAsksViewSet)
router.register(r'my_listings', rest_views.MyListingsViewSet, base_name='MyListings')
router.register(r'listings', rest_views.ListingsViewSet, base_name='Listings')
router.register(r'saved_searches', rest_views.SavedSearchViewSet, base_name='SavedSearches')
router.register(r'users', rest_views.UserViewSet, base_name='User')
router.register(r'favorite_asks', rest_views.FavoriteAskViewSet, base_name='FavoriteAsk')
router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)


router.register(r'sms_corrections', rest_views.SMSViewSet, base_name='IncomingSMS')


admin.autodiscover()
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^celery_check/(?P<task_id>.+)$', views.check_task_url),
    url(r'^main-handler/$', views.main_handler),

    ### REST
    url(r'^rest-api/', include(router.urls)),
    url(r'^rest-api/user/get_or_create/', rest_views.get_or_create_user),
    url(r'^rest-api/send-notifications/$', views.send_notifications),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

from django.conf import settings

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns