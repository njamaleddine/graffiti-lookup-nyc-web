"""Geocoding service for NYC addresses."""

from typing import NamedTuple

from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim

from graffiti_data_pipeline.config import (
    REQUEST_ERROR_WAIT_SECONDS,
    REQUEST_MAX_RETRIES,
    REQUEST_MIN_DELAY_SECONDS,
    REQUEST_TIMEOUT,
    REQUEST_USER_AGENT,
)
from graffiti_data_pipeline.geocode.sanitize import normalize_street_name
from graffiti_data_pipeline.logger import get_logger

logger = get_logger(__name__)


class Coordinates(NamedTuple):
    """A geographic coordinate pair."""

    latitude: float
    longitude: float


class Geocoder:
    """Resolves addresses to geographic coordinates.

    Wraps a geocoding callable with an in-memory cache to avoid
    redundant network calls.  Addresses are normalized for NYC
    street-naming conventions before lookup.

    The :attr:`cache` property exposes the underlying dict so
    callers can persist it between runs.

    Usage::

        geocoder = Geocoder.from_config()
        coords = geocoder.geocode("123 MAIN ST")
        if coords:
            print(coords.latitude, coords.longitude)
    """

    def __init__(self, geocode_fn, cache=None):
        self._geocode_fn = geocode_fn
        self._cache = cache if cache is not None else {}

    def __repr__(self):
        return f"{type(self).__name__}(cache_size={len(self._cache)})"

    @classmethod
    def from_config(
        cls,
        cache=None,
        user_agent=REQUEST_USER_AGENT,
        timeout=REQUEST_TIMEOUT,
        min_delay_seconds=REQUEST_MIN_DELAY_SECONDS,
        max_retries=REQUEST_MAX_RETRIES,
        error_wait_seconds=REQUEST_ERROR_WAIT_SECONDS,
    ):
        """Create a production Geocoder from project configuration.

        Pass *cache* to seed the geocoder with previously persisted
        results.  When omitted, starts with an empty cache.
        """
        geolocator = Nominatim(user_agent=user_agent, timeout=timeout)
        geocode_fn = RateLimiter(
            geolocator.geocode,
            min_delay_seconds=min_delay_seconds,
            max_retries=max_retries,
            error_wait_seconds=error_wait_seconds,
        )
        return cls(geocode_fn, cache)

    @property
    def cache(self):
        """The current in-memory geocode cache."""
        return self._cache

    def geocode(self, address):
        """Resolve *address* to :class:`Coordinates`, or ``None``.

        Returns cached coordinates on a hit.  On a cache miss the
        street name is normalized, the geocoding service is queried,
        and the result is stored in the cache.
        """
        if not isinstance(address, str) or not address.strip():
            logger.warning(f"Invalid address input: {address!r}")
            return None

        cached = self._cache.get(address)
        if cached is not None:
            logger.debug(f"Cache hit: {address} -> {cached}")
            return Coordinates(*cached)

        return self._resolve(address)

    def _resolve(self, address):
        """Query the geocoding service and cache a successful result."""
        full_address = f"{normalize_street_name(address)}, NY, USA"
        logger.info(f"Geocoding: {full_address}")

        try:
            location = self._geocode_fn(full_address)
        except (GeocoderTimedOut, GeocoderUnavailable) as exc:
            logger.error(f"Geocoding error: {exc}")
            return None

        if location is None:
            logger.warning(f"No coordinates found for {full_address}")
            return None

        coords = Coordinates(location.latitude, location.longitude)
        self._cache[address] = (coords.latitude, coords.longitude)
        logger.info(
            f"Found: {full_address} -> ({coords.latitude}, {coords.longitude})"
        )
        return coords


def geocode_service_requests(service_requests, geocoder):
    """Add coordinates to service requests that are missing them.

    .. warning::

        Mutates each dict in *service_requests* **in place**,
        inserting ``latitude`` and ``longitude`` keys for every
        successfully geocoded address.

    Also backfills the geocoder's cache from service requests that
    already have coordinates, keeping the cache in sync without
    extra network calls.

    Returns ``True`` if the cache was modified (new geocoding or
    backfill), ``False`` otherwise.
    """
    cache_changed = False

    for request in service_requests:
        if not isinstance(request, dict):
            continue

        address = request.get("address")
        if _needs_geocoding(request):
            coords = geocoder.geocode(address)
            if coords is not None:
                request["latitude"] = coords.latitude
                request["longitude"] = coords.longitude
                cache_changed = True
        elif _can_backfill_cache(request, address, geocoder.cache):
            geocoder.cache[address] = (
                request["latitude"],
                request["longitude"],
            )
            cache_changed = True

    return cache_changed


def _needs_geocoding(request):
    """Return True if the request dict lacks coordinate keys."""
    return "latitude" not in request and "longitude" not in request


def _can_backfill_cache(request, address, cache):
    """Return True if the request has coords but the cache doesn't."""
    return (
        isinstance(address, str)
        and address.strip()
        and "latitude" in request
        and "longitude" in request
        and address not in cache
    )
