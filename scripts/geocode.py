import json
import os

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


CACHE_FILE = "public/geocode-cache.json"
DATA_FILE = "public/graffiti-lookups.json"


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
        return geocode_cache[address]

    # Append NY to improve geocoding accuracy for NYC addresses
    full_address = f"{address}, NY, USA"
    location = geocode(full_address)

    if location:
        geocode_cache[address] = (location.latitude, location.longitude)
        return geocode_cache[address]

    return None, None


def main():
    geocode_cache = load_cache()
    data = load_service_requests()

    geolocator = Nominatim(user_agent="graffiti-lookup-nyc-web")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

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
