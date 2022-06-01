from django.core.management.base import BaseCommand

from agrotrade.clearing import vcg_clearing


class Command(BaseCommand):
    help = 'Runs the clearing algorithm'

    def handle(self, *args, **options):
        vcg_clearing.main()