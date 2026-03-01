#!/usr/bin/env python3
"""Entry point for geocoding graffiti lookup addresses."""

from graffiti_data_pipeline.config import (
    GEOCODE_CACHE_FILE,
    GRAFFITI_LOOKUPS_FILE,
)
from graffiti_data_pipeline.geocode.geocoder import (
    Geocoder,
    geocode_service_requests,
)
from graffiti_data_pipeline.logger import get_logger
from graffiti_data_pipeline.storages import JsonFile

logger = get_logger(__name__)


def main():
    logger.info("Starting geocoding process")

    lookups = JsonFile(GRAFFITI_LOOKUPS_FILE, default_data=[])
    service_requests = lookups.load()
    logger.info(f"Loaded {len(service_requests)} service requests")

    cache_store = JsonFile(GEOCODE_CACHE_FILE)
    geocoder = Geocoder.from_config(cache=cache_store.load())

    try:
        new_coordinates = geocode_service_requests(service_requests, geocoder)
        if new_coordinates:
            cache_store.save(geocoder.cache)
        lookups.save(service_requests)
    except Exception as exc:
        logger.error(f"Error during geocoding: {exc}")
    finally:
        logger.info("Geocoding complete")


if __name__ == "__main__":
    main()
