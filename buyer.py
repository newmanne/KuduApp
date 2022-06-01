from .geocoding import get_address

from .models import TraderBids
from django.db import transaction


def make_bid(userprofile, produce, quantity, price, location=None, tags=None, contact_number=None,
             **kwargs):

    '''All making of bids should go through this function'''


    with transaction.atomic():
        bid = TraderBids.objects.create(
            owner=userprofile,
            produce=produce,
            quantity=quantity,
            price=price,
            location=location,
            address=get_address(location) if location is not None else {},
            contact_number=contact_number,
            **kwargs
        )

        if tags is not None:
            bid.tags.add(*tags)

    return bid