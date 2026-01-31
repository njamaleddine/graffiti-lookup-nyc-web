import json
import os
import re

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


CACHE_FILE = "public/geocode-cache.json"
DATA_FILE = "public/graffiti-lookups.json"

# Street type patterns to match
STREET_TYPES = r"(STREET|ST|AVENUE|AVE|ROAD|RD|DRIVE|DR|PLACE|PL|BOULEVARD|BLVD|LANE|LN|COURT|CT|WAY|TERRACE|TER)"


def get_ordinal_suffix(number):
    """Convert a number to its ordinal suffix (1->1st, 2->2nd, 3->3rd, etc.)"""
    number = int(number)
    if 11 <= number % 100 <= 13:
        return f"{number}TH"
    suffix = {1: "ST", 2: "ND", 3: "RD"}.get(number % 10, "TH")
    return f"{number}{suffix}"


def normalize_street_name(address):
    """Convert '3 STREET' to '3RD STREET', etc."""
    pattern = rf"(\d+)\s+{STREET_TYPES}"

    def replace_match(match):
        number = match.group(1)
        street_type = match.group(2)
        return f"{get_ordinal_suffix(number)} {street_type}"

    return re.sub(pattern, replace_match, address, flags=re.IGNORECASE)


def load_cache(cache_file=CACHE_FILE):
    if os.path.exists(cache_file):
        with open(cache_file) as file:
            return json.load(file)
    return {}


def save_cache(cache, cache_file=CACHE_FILE):
    with open(cache_file, "w") as file:
        json.dump(cache, file, indent=2)


def load_service_requests(data_file=DATA_FILE):
    with open(data_file) as file:
        return json.load(file)


def save_data(data, data_file=DATA_FILE):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=2)


def geocode_address(address, geocode, geocode_cache):
    if address in geocode_cache:
        cached = geocode_cache[address]
        print(f"Cache hit: {address} -> {cached}")
        return cached

    try:
        # Normalize street names (e.g., "83 STREET" -> "83RD STREET")
        normalized_address = normalize_street_name(address)
        # Append NY to improve geocoding accuracy for NYC addresses
        full_address = f"{normalized_address}, NY, USA"
        print(f"Geocoding: {full_address}")
        location = geocode(full_address)

        if location:
            geocode_cache[address] = (location.latitude, location.longitude)
            print(
                f"Found coordinates for {full_address}: {location.latitude}, {location.longitude}"
            )
            return geocode_cache[address]
        else:
            print(f"No coordinates found for {full_address}")
    except (GeocoderTimedOut, GeocoderUnavailable) as error:
        print(f"Error: {error}")

    return None, None


def main():
    geocode_cache = load_cache()
    data = load_service_requests()

    geolocator = Nominatim(user_agent="graffiti-lookup-nyc-web", timeout=10)
    geocode = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=1.5,
        max_retries=3,
        error_wait_seconds=5.0,
    )

    for service_request in data:
        if "latitude" not in service_request or "longitude" not in service_request:
            latitude, longitude = geocode_address(
                service_request["address"], geocode, geocode_cache
            )

            if latitude and longitude:
                service_request["latitude"] = latitude
                service_request["longitude"] = longitude

    save_cache(geocode_cache)
    save_data(data)


if __name__ == "__main__":
    main()
