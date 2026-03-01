"""
Graffiti Service Request Model

Represents a single graffiti service request and provides methods to extract features.
"""

from typing import List, Dict, Any
import pandas
from graffiti_data_pipeline.config import (
    GRAFFITI_CLEANED_STATUS,
    GRAFFITI_COMPLETE_STATUSES,
    NYC_BOROUGHS,
)


class GraffitiServiceRequest:
    def __init__(self, record: Dict[str, Any]):
        self.record = record
        self.address = record.get("address", "")
        self.last_updated = record.get("last_updated", "1970-01-01")
        self.created = record.get("created", "1970-01-01")
        self.status = record.get("status", "unknown")
        self.latitude = record.get("latitude", 0.0)
        self.longitude = record.get("longitude", 0.0)
        self.unique_key = record.get("unique_key", self.address)

    def get_borough(self) -> str:
        address_lower = self.address.lower()
        for borough in NYC_BOROUGHS:
            if borough in address_lower:
                return borough
        return "unknown"

    def get_last_tag_date(self) -> pandas.Timestamp:
        return pandas.to_datetime(self.last_updated)

    def get_created_tag_date(self) -> pandas.Timestamp:
        return pandas.to_datetime(self.created)

    def get_days_since_last_tag(self) -> int:
        return (pandas.Timestamp.now() - self.get_last_tag_date()).days

    def get_response_time_days(self) -> int:
        return (self.get_last_tag_date() - self.get_created_tag_date()).days

    def get_created_day_of_week(self) -> int:
        """Day of week the report was created (0=Monday, 6=Sunday)."""
        return self.get_created_tag_date().dayofweek

    def get_created_month(self) -> int:
        """Month the report was created (1-12)."""
        return self.get_created_tag_date().month

    def get_times_cleaned(
        self, address_index: Dict[str, List["GraffitiServiceRequest"]]
    ) -> int:
        """Count how many times this address was actually cleaned.

        Only counts requests with the specific cleaned status, not other
        complete statuses like 'No graffiti on property'.
        """
        same_address = address_index.get(self.address, [])
        return sum(1 for req in same_address if req.status == GRAFFITI_CLEANED_STATUS)

    def get_resolution_velocity(
        self, address_index: Dict[str, List["GraffitiServiceRequest"]]
    ) -> Any:
        """Average days to resolve past completed requests at this address.

        Returns the mean resolution time (created→last_updated) across
        completed requests whose completion date is *before* this
        request's created date.  ``None`` if there is no prior history.
        """
        created_date = self.get_created_tag_date()
        same_address = address_index.get(self.address, [])
        past_completed = [
            req
            for req in same_address
            if req.status in GRAFFITI_COMPLETE_STATUSES
            and pandas.to_datetime(req.last_updated) < created_date
        ]
        if not past_completed:
            return None
        total_days = sum(
            (
                pandas.to_datetime(req.last_updated) - pandas.to_datetime(req.created)
            ).days
            for req in past_completed
        )
        return round(total_days / len(past_completed))

    def get_recurrence_window(
        self, address_index: Dict[str, List["GraffitiServiceRequest"]]
    ) -> Any:
        """Days until the next report at this address, or None.

        Unlike the binary ``tagged_again``, this gives a continuous
        target the regressor can learn from.
        """
        created_date = self.get_created_tag_date()
        same_address = address_index.get(self.address, [])
        later_reports = [
            req
            for req in same_address
            if pandas.to_datetime(req.created) > created_date
        ]
        if later_reports:
            next_report = min(
                later_reports, key=lambda x: pandas.to_datetime(x.created)
            )
            return (pandas.to_datetime(next_report.created) - created_date).days
        return None

    def get_resolution_time(
        self, address_index: Dict[str, List["GraffitiServiceRequest"]]
    ) -> Any:
        """Days from created to the first complete status at this address.

        Returns None if no request at this address has reached a
        complete status yet.
        """
        same_address = address_index.get(self.address, [])
        completed = [
            req
            for req in same_address
            if req.status in GRAFFITI_COMPLETE_STATUSES
            and pandas.to_datetime(req.last_updated) >= self.get_created_tag_date()
        ]
        if completed:
            earliest = min(completed, key=lambda x: pandas.to_datetime(x.last_updated))
            days = (
                pandas.to_datetime(earliest.last_updated) - self.get_created_tag_date()
            ).days
            return max(days, 0)
        return None

    def get_tag_count_at_location(
        self, address_index: Dict[str, List["GraffitiServiceRequest"]]
    ) -> int:
        """Count requests at this address using a pre-built index."""
        return len(address_index.get(self.address, []))

    def get_tagged_again(
        self, address_index: Dict[str, List["GraffitiServiceRequest"]]
    ) -> int:
        return 1 if self.get_tag_count_at_location(address_index) > 1 else 0

    def get_status_code(self, status_categories: Dict[str, int]) -> int:
        if self.status not in status_categories:
            status_categories[self.status] = len(status_categories)
        return status_categories[self.status]

    def is_cleaned(self, cleaned_keywords: List[str]) -> int:
        """Return 1 if the status contains any of the cleaned keywords."""
        return int(any(keyword in self.status for keyword in cleaned_keywords))

    def get_time_to_next_update(
        self, address_index: Dict[str, List["GraffitiServiceRequest"]]
    ) -> Any:
        """Days until the next request at this address, or None."""
        last_tag_date = self.get_last_tag_date()
        same_address_requests = address_index.get(self.address, [])
        next_updates = [
            req
            for req in same_address_requests
            if pandas.to_datetime(req.created) > last_tag_date
        ]
        if next_updates:
            next_update = min(next_updates, key=lambda x: pandas.to_datetime(x.created))
            return (pandas.to_datetime(next_update.created) - last_tag_date).days
        return None

    def to_feature_dict(
        self,
        status_categories: Dict[str, int],
        cleaned_keywords: List[str],
        address_index: Dict[str, List["GraffitiServiceRequest"]],
    ) -> Dict[str, Any]:
        """Build a feature dictionary using a pre-built address index."""
        return {
            "days_since_last_tag": self.get_days_since_last_tag(),
            "borough": self.get_borough(),
            "total_tags": self.get_tag_count_at_location(address_index),
            "response_time": self.get_response_time_days(),
            "created_day_of_week": self.get_created_day_of_week(),
            "created_month": self.get_created_month(),
            "times_reported": self.get_tag_count_at_location(address_index),
            "times_cleaned": self.get_times_cleaned(address_index),
            "resolution_velocity": self.get_resolution_velocity(address_index),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status_code": self.get_status_code(status_categories),
            "tagged_again": self.get_tagged_again(address_index),
            "cleaned": self.is_cleaned(cleaned_keywords),
            "time_to_next_update": self.get_time_to_next_update(address_index),
            "recurrence_window": self.get_recurrence_window(address_index),
            "resolution_time": self.get_resolution_time(address_index),
            "index": self.unique_key,
        }
