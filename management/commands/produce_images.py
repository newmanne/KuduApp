from django.core.management.base import BaseCommand
import glob
from agrotrade.models import ProduceDefinition

class Command(BaseCommand):
    help = 'Fix phone numbers'

    def handle(self, *args, **options):
        picture_files = glob.glob('./vue_app/src/assets/crops/*.jpg')
        for picture_file in picture_files:
            p = picture_file.split('/')[-1].strip('.jpg')
            x = ProduceDefinition.objects.get(pk=p)
            x.active = True
            x.image_path = 'crops/' + str(x.pk) + '.jpg'
            x.save()