from datetime import datetime, timedelta
import argparse

from geocode.logger import get_logger
from geocode.storages import JsonFile
from geocode.config import (
    GRAFFITI_COMPLETE_STATUSES,
    GRAFFITI_FILTER_ACTIVE_SERVICE_REQUESTS,
    GRAFFITI_LOOKUPS_FILE,
    GRAFFITI_RECENT_REQUEST_DAYS,
)


logger = get_logger(__name__)


def was_recently_updated(last_updated: str, days=GRAFFITI_RECENT_REQUEST_DAYS):
    """Check if the last_updated date string is within the specified number of days from today."""
    try:
        last_updated_date = datetime.strptime(last_updated, "%Y-%m-%d")
        return last_updated_date >= datetime.now() - timedelta(days=days)
    except Exception:
        return False


def get_active_service_requests(service_requests, days=GRAFFITI_RECENT_REQUEST_DAYS):
    """
    Returns only active service requests from the provided list.
    Removes requests that are complete or not recently updated.
    """

    active_service_requests = []

    for request in service_requests:
        status = request.get("status")
        last_updated = request.get("last_updated")
        if status not in GRAFFITI_COMPLETE_STATUSES and was_recently_updated(
            last_updated, days
        ):
            active_service_requests.append(request)

    return active_service_requests


def print_graffiti_service_request_ids(
    json_path,
    enable_filter=False,
    days=GRAFFITI_RECENT_REQUEST_DAYS,
):
    """
    Prints active graffiti service_request IDs as a comma-separated string.
    """
    active_requests = JsonFile(json_path).load()

    if enable_filter:
        active_requests = get_active_service_requests(active_requests, days)

    ids = [
        request["service_request"]
        for request in active_requests
        if "service_request" in request
    ]

    print(",".join(ids), end="")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Print graffiti service request IDs.")
    parser.add_argument(
        "--filter-active",
        action="store_true",
        default=GRAFFITI_FILTER_ACTIVE_SERVICE_REQUESTS,
        help="Filter only active service requests",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=GRAFFITI_RECENT_REQUEST_DAYS,
        help="Number of days for recency filter",
    )
    parser.add_argument(
        "--json-path",
        type=str,
        default=GRAFFITI_LOOKUPS_FILE,
        help="Path to graffiti service requests JSON file",
    )
    args = parser.parse_args()

    print_graffiti_service_request_ids(
        args.json_path,
        enable_filter=args.filter_active,
        days=args.days,
    )
