import time
from contextlib import contextmanager

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.gis.geos import Polygon
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from push_notifications.models import GCMDevice

from agrotrade.models import SavedSearch, FarmerAsks
from .utils import *

logger = get_task_logger(__name__)

LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes

NEW_UPDATE_LOCK_KEY = 'NEW_UPDATE'
EXPIRE_LOCK_KEY = 'EXPIRE_BIDS_ASK'
kudu_ai_BID_KEY = 'kudu_ai_BID'


@contextmanager
def redis_lock_nonblocking(name):
    ## TODO: Probably best to replace this with the cache's connection if possible...
    r = StrictRedis(connection_pool=settings.REDIS_CONN_POOL)
    lock_object = r.lock(name, timeout=LOCK_EXPIRE)
    acquired = lock_object.acquire(blocking=False)
    try:
        yield acquired
    finally:
        if acquired:
            lock_object.release()


@shared_task
def scan_for_active():
    """Scan for asks that have recently be added and need to be set to active"""
    with redis_lock_nonblocking(NEW_UPDATE_LOCK_KEY) as acquired:
        if not acquired:
            logger.debug('Another worker is already performing performing new update, leaving')
            return

        # When a bid or ask is created "New" = True. Celery selects New = True, sets New = False and sets Active = True.
        new_asks_qs = FarmerAsks.objects.filter(new=True)
        ask_count = new_asks_qs.update(new=False, active=True)
        if ask_count > 0:
            logger.info("Processed %d new asks" % (ask_count))


@shared_task
def mark_inactive():
    """Mark bids / asks that have "expired" from the system"""
    with redis_lock_nonblocking(EXPIRE_LOCK_KEY) as acquired:
        if not acquired:
            logger.debug('Another worker is already performing expiry, leaving')
            return

        # Expire things that do not have an ongoing "managed" match, meaning one that would be followed up on (meaning seller is agrinet)
        ask_count = FarmerAsks.objects.filter(FarmerAsks.expired_q(), active=True).update(active=False)
        if ask_count > 0:
            logger.info("Expired %d asks" % (ask_count))


@shared_task
def check_new_saved_search_matches():
    for saved_search in SavedSearch.objects.all():
        filters = {
            'created_date__gte': saved_search.last_seen_date,
            'active': True,
            'produce__in': saved_search.produce.all(),
            'price__range': (saved_search.min_price, saved_search.max_price),
            'quantity__range': (saved_search.min_quantity, saved_search.max_quantity)
            # time__lte=saved_search.time,
        }

        if saved_search.sw_latlng and saved_search.ne_latlng:
            filters['location__within'] = Polygon.from_bbox(
                (saved_search.sw_latlng[0], saved_search.sw_latlng[1],
                 saved_search.ne_latlng[0], saved_search.ne_latlng[1]))

        ask_query_set = FarmerAsks.objects.filter(**filters)

        if ask_query_set.exists():
            saved_search.state = SavedSearch.SEARCH_TO_NOTIFY
            saved_search.save()

            GCMDevice.objects.filter(user=saved_search.owner.user).send_message(
                "We have found products you might be interested in: " + saved_search.produce.all()[0].display_name,
                extra={
                    'title': 'New matches for your search',
                    'click_action': "FCM_PLUGIN_ACTIVITY",
                    'pk': saved_search.pk
                }
            )


@shared_task
def complete_asks_address():
    geolocator = Nominatim(user_agent="Kudu")

    for farmer_ask in FarmerAsks.objects.filter(address={}).exclude(location=None):
        try:
            farmer_ask.address = geolocator.reverse(farmer_ask.location).raw['address']
            time.sleep(1)
        except GeocoderTimedOut as e:
            farmer_ask.address = {}
        farmer_ask.save()
