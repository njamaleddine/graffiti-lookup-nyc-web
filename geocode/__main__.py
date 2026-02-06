#!/usr/bin/env python3
"""Main script to geocode graffiti lookup addresses."""

from geocode.geocoder import geocode_addresses
from geocode.logger import get_logger
from geocode.config import GRAFFITI_LOOKUPS_FILE
from geocode.storages.json import JsonFile

logger = get_logger(__name__)


def main():
    logger.info("Starting geocoding process")

    graffiti_service_requests_cache = JsonFile(GRAFFITI_LOOKUPS_FILE)
    service_requests = graffiti_service_requests_cache.load()

    logger.info(f"Loaded {len(service_requests)} service requests")

    try:
        geocode_addresses(service_requests)
        graffiti_service_requests_cache.save(service_requests)
    except Exception as e:
        logger.error(f"Error during geocoding or saving: {e}")
    finally:
        logger.info("Geocoding complete")


if __name__ == "__main__":
    main()
