from django.core.management.base import BaseCommand

from agrotrade.models import Parish
from django.contrib.gis.geos import GEOSGeometry, Point


class Command(BaseCommand):
    help = 'Runs the clearing algorithm'

    def handle(self, *args, **options):
        for parish in Parish.objects.all():
            parish.latlng = Point(parish.lat, parish.lng)
            parish.save()