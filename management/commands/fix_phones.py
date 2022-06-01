from django.core.management.base import BaseCommand
from phonenumber_field.phonenumber import PhoneNumber
import phonenumbers

from agrotrade.models import UserProfile

class Command(BaseCommand):
    help = 'Fix phone numbers'

    def handle(self, *args, **options):
        duplicate_users = 0
        invalid = 0
        exception = 0
        changed = 0
        pns = set()
        for up in UserProfile.objects.all():
            pn = str(up.phone_number)
            if pn.startswith('0'):
                pn = '+256' + pn[1:]
            if not pn.startswith('+'):
                pn = '+' + pn

            try:
                z = phonenumbers.parse(pn, None)
                if not phonenumbers.is_valid_number(z):
                    invalid += 1
                    continue

                if pn in pns:
                    duplicate_users += 1
                    continue

                if up.phone_number != pn:
                    print(f"Changing {up.phone_number} to {pn}")
                    up.phone_number = pn
                    up.save()
                    changed += 1

                pns.add(pn)

            except Exception as e:
                exception += 1
                # print('Exception', up.phone_number, pn)
                # print(e)


        print("Duplicate", duplicate_users)
        print("Invalid", invalid)
        print("Exception", exception)
        print("Changed", changed)