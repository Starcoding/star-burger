import requests
from django.conf import settings

from .models import Coordinates


def fetch_coordinates_from_geocoder(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": settings.YANDEX_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return None
    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    Coordinates.objects.create(address=address, longtitude=lon, latitude=lat)
    return lon, lat


def fetch_coordinates(address, coordinates):
    for coordinate in coordinates:
        if coordinate.address == address:
            lon = coordinate.longtitude
            lat = coordinate.latitude
            return lon, lat
    else:
        return fetch_coordinates_from_geocoder(address)