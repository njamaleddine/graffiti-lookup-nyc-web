from datetime import datetime, timedelta
import os

from geocode.logger import get_logger
from geocode.storages import JsonFile
from geocode.constants import (
    GRAFFITI_LOOKUPS_FILE,
    GRAFFITI_COMPLETE_STATUSES,
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
    json_path, enable_filter=os.getenv("FILTER_ACTIVE_SERVICE_REQUESTS") == "True"
):
    """
    Prints active graffiti service_request IDs as a comma-separated string.
    """
    active_service_requests = JsonFile(json_path).load()

    if enable_filter:
        active_service_requests = get_active_service_requests(active_service_requests)

    ids = [
        request["service_request"]
        for request in active_service_requests
        if "service_request" in request
    ]

    print(",".join(ids), end="")


if __name__ == "__main__":
    print_graffiti_service_request_ids(GRAFFITI_LOOKUPS_FILE)
