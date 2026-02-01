#!/usr/bin/env python3
"""Main script to geocode graffiti lookup addresses."""

import json

from geocode.geocoder import geocode_addresses
from geocode.logger import get_logger

logger = get_logger(__name__)

DATA_FILE = "public/graffiti-lookups.json"


def load_service_requests(data_file=DATA_FILE):
    with open(data_file) as file:
        return json.load(file)


def save_service_requests(data, data_file=DATA_FILE):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=2)


def main():
    logger.info("Starting geocoding process")
    data = load_service_requests()

    logger.info(f"Loaded {len(data)} service requests")

    geocode_addresses(data)
    save_service_requests(data)

    logger.info("Geocoding complete")


if __name__ == "__main__":
    main()
