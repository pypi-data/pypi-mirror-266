#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#  IBIS is a registered trademark
#
import os
from urllib.parse import urlparse

from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.geocoders import Nominatim

nominatim_url = f"{os.environ.get('IBIS_NOMINATIM_URL')}"
nominatim_url = urlparse(nominatim_url).netloc
geolocator = Nominatim(user_agent="ibis", scheme="http", domain=nominatim_url)


def get_address_by_coordinates(latitude, longitude, exactly_one=True):
    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=exactly_one)
        if not location:
            return "No address found for this location."
        address = location.address
        return address
    except GeocoderTimedOut:
        return "GeocoderTimedOut: Failed to reach the server."


def get_coordinates_for_address(address):
    """
    Geocode an address using a custom Nominatim server.

    :param address: The address to geocode.
    :return: A dictionary with the location's latitude, longitude, and full address, or a message if an error occurs.
    """
    try:
        location = geolocator.geocode(address)

        # Check if location was found
        if location:
            return {
                "Address": location.address,
                "Latitude": location.latitude,
                "Longitude": location.longitude
            }
        else:
            return "Location not found."

    except GeocoderTimedOut:
        return "GeocoderTimedOut: Request timed out."
    except GeocoderServiceError as e:
        return f"GeocoderServiceError: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
