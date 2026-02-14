"""Geocoding functionality using Nominatim."""

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from geocode.logger import get_logger
from geocode.sanitize import normalize_street_name
from geocode.storages import JsonFile
from geocode.config import (
    GEOCODE_CACHE_FILE,
    REQUEST_USER_AGENT,
    REQUEST_TIMEOUT,
    REQUEST_MIN_DELAY_SECONDS,
    REQUEST_MAX_RETRIES,
    REQUEST_ERROR_WAIT_SECONDS,
)

logger = get_logger(__name__)


def geocode_address(address, geocode_fn, cache):
    """Geocode a single address, using cache if available."""
    if not isinstance(address, str) or not address.strip():
        return (None, None)

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

    return (None, None)


def geocode_addresses(
    service_requests,
    cache_file=GEOCODE_CACHE_FILE,
    user_agent=REQUEST_USER_AGENT,
    timeout=REQUEST_TIMEOUT,
    min_delay_seconds=REQUEST_MIN_DELAY_SECONDS,
    max_retries=REQUEST_MAX_RETRIES,
    error_wait_seconds=REQUEST_ERROR_WAIT_SECONDS,
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
    geocode_cache = JsonFile(cache_file)
    geocode_data = geocode_cache.load()

    geolocator = Nominatim(user_agent=user_agent, timeout=timeout)
    geocode_fn = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=min_delay_seconds,
        max_retries=max_retries,
        error_wait_seconds=error_wait_seconds,
    )

    addresses_geocoded = False

    for service_request in service_requests:
        # Only geocode if 'latitude' and 'longitude' are missing
        if (
            isinstance(service_request, dict)
            and "latitude" not in service_request
            and "longitude" not in service_request
        ):
            address = service_request.get("address")
            latitude, longitude = geocode_address(address, geocode_fn, geocode_data)

            if latitude is not None and longitude is not None:
                service_request["latitude"] = latitude
                service_request["longitude"] = longitude
                addresses_geocoded = True

    if addresses_geocoded:
        geocode_cache.save(geocode_data)
    return service_requests
