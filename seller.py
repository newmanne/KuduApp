'''
@author: rkayondo
'''

from .models import FarmerAsks
from django.db import transaction
from .geocoding import get_address


def make_ask(userprofile, produce, quantity, price, delivery, payment_methods, location, tags, contact_number, **kwargs):
    '''All making asks should go through this function'''

    address = {}
    if location is not None:
        address = get_address(location),

    with transaction.atomic():
        ask = FarmerAsks.objects.create(
            owner=userprofile,
            produce=produce,
            quantity=quantity,
            price=price,
            delivery=delivery,
            location=location,
            address=address,
            contact_number=contact_number,
            **kwargs
        )

        if tags is not None:
            ask.tags.add(*tags)

        if payment_methods is not None:
            ask.payment_methods.add(*payment_methods)

    return ask