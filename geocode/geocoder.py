"""Geocoding functionality using Nominatim."""

import json
import os

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from geocode.logger import get_logger
from geocode.sanitize import normalize_street_name

logger = get_logger(__name__)


CACHE_FILE = "public/geocode-cache.json"
USER_AGENT = "graffiti-lookup-nyc-web"
TIMEOUT = 10
MIN_DELAY_SECONDS = 1.5
MAX_RETRIES = 3
ERROR_WAIT_SECONDS = 5.0


def load_geocode_cache(cache_file):
    if os.path.exists(cache_file):
        with open(cache_file) as file:
            return json.load(file)
    return {}


def save_geocode_cache(cache, cache_file):
    with open(cache_file, "w") as file:
        json.dump(cache, file, indent=2)


def geocode_address(address, geocode_fn, cache):
    """Geocode a single address, using cache if available."""
    if address in cache:
        cached = cache[address]
        logger.debug(f"Cache hit: {address} -> {cached}")
        return cached

    try:
        normalized_address = normalize_street_name(address)
        # Append NY to improve geocoding accuracy for NYC addresses
        full_address = f"{normalized_address}, NY, USA"
        logger.info(f"Geocoding: {full_address}")
        location = geocode_fn(full_address)

        if location:
            cache[address] = (location.latitude, location.longitude)
            logger.info(
                f"Found coordinates for {full_address}: {location.latitude}, {location.longitude}"
            )
            return cache[address]
        else:
            logger.warning(f"No coordinates found for {full_address}")
    except (GeocoderTimedOut, GeocoderUnavailable) as error:
        logger.error(f"Geocoding error: {error}")

    return None, None


def geocode_addresses(
    service_requests,
    cache_file=CACHE_FILE,
    user_agent=USER_AGENT,
    timeout=TIMEOUT,
    min_delay_seconds=MIN_DELAY_SECONDS,
    max_retries=MAX_RETRIES,
    error_wait_seconds=ERROR_WAIT_SECONDS,
):
    """
    Geocode addresses in a list of service request dictionaries.

    Args:
        service_requests: List of dictionaries with 'address' key
        cache_file: Path to geocode cache file
        user_agent: User agent for Nominatim
        timeout: Request timeout in seconds
        min_delay_seconds: Minimum delay between requests
        max_retries: Number of retries on failure
        error_wait_seconds: Wait time after error

    Returns:
        Updated service_requests with latitude/longitude added
    """
    cache = load_geocode_cache(cache_file)

    geolocator = Nominatim(user_agent=user_agent, timeout=timeout)
    geocode_fn = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=min_delay_seconds,
        max_retries=max_retries,
        error_wait_seconds=error_wait_seconds,
    )

    for service_request in service_requests:
        if "latitude" not in service_request or "longitude" not in service_request:
            latitude, longitude = geocode_address(
                service_request["address"], geocode_fn, cache
            )

            if latitude and longitude:
                service_request["latitude"] = latitude
                service_request["longitude"] = longitude

    save_geocode_cache(cache, cache_file)
    return service_requests
