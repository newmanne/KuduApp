from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

import googlemaps

def get_address_nominatim(location):
    geolocator = Nominatim(user_agent="Kudu")

    try:
        address = geolocator.reverse(location).raw['address']
    except GeocoderTimedOut as e:
        address = {}
    return address

def get_address_google(location):
    gmaps = googlemaps.Client(key='TODO')
    try:
        reverse_geocode_result = gmaps.reverse_geocode(location)
        if len(reverse_geocode_result) > 0:
            address = reverse_geocode_result[0]
    except:
        address = {}

    return address


def get_address(location):
    return get_address_google(location)
