"""
Graffiti Service Request Model

Represents a single graffiti service request and provides methods to extract features.
"""

from typing import List, Dict, Any
import pandas
from graffiti_data_pipeline.config import NYC_BOROUGHS


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

    def get_tag_count_at_location(
        self, all_requests: List["GraffitiServiceRequest"]
    ) -> int:
        return sum(1 for req in all_requests if req.address == self.address)

    def get_tagged_again(self, all_requests: List["GraffitiServiceRequest"]) -> int:
        return 1 if self.get_tag_count_at_location(all_requests) > 1 else 0

    def get_status_code(self, status_categories: Dict[str, int]) -> int:
        if self.status not in status_categories:
            status_categories[self.status] = len(status_categories)
        return status_categories[self.status]

    def is_cleaned(self, cleaned_keywords: List[str]) -> int:
        # Boost cleaning probability for 'Site to be cleaned.'
        if "Site to be cleaned." in self.status:
            return 1
        return int(any(keyword in self.status for keyword in cleaned_keywords))

    def get_time_to_next_update(
        self, all_requests: List["GraffitiServiceRequest"]
    ) -> Any:
        last_tag_date = self.get_last_tag_date()
        next_updates = [
            req
            for req in all_requests
            if req.address == self.address
            and pandas.to_datetime(req.created) > last_tag_date
        ]
        if next_updates:
            next_update = min(next_updates, key=lambda x: pandas.to_datetime(x.created))
            return (pandas.to_datetime(next_update.created) - last_tag_date).days
        else:
            return None

    def to_feature_dict(
        self,
        status_categories: Dict[str, int],
        cleaned_keywords: List[str],
        all_requests: List["GraffitiServiceRequest"],
    ) -> Dict[str, Any]:
        return {
            "days_since_last_tag": self.get_days_since_last_tag(),
            "borough": self.get_borough(),
            "total_tags": self.get_tag_count_at_location(all_requests),
            "response_time": self.get_response_time_days(),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status_code": self.get_status_code(status_categories),
            "tagged_again": self.get_tagged_again(all_requests),
            "cleaned": self.is_cleaned(cleaned_keywords),
            "time_to_next_update": self.get_time_to_next_update(all_requests),
            "index": self.unique_key,
        }
