from django.core.management.base import BaseCommand

from agrotrade.models import Parish, FarmerAsks
from django.contrib.gis.geos import GEOSGeometry, Point


class Command(BaseCommand):
    help = 'Runs the clearing algorithm'

    def handle(self, *args, **options):
        for ask in FarmerAsks.objects.all():
            parish = ask.owner.parish
            if parish is not None:
                ask.location = parish.latlng
                ask.save()
