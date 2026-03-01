"""
Feature Engineering for Graffiti Prediction

Provides functions to engineer features from graffiti service requests.
"""

from collections import defaultdict
from typing import Dict, List

import pandas

from graffiti_data_pipeline.prediction.request import GraffitiServiceRequest


def _build_address_index(
    requests: List[GraffitiServiceRequest],
) -> Dict[str, List[GraffitiServiceRequest]]:
    """Map each address to its list of requests for O(1) lookup."""
    index: Dict[str, List[GraffitiServiceRequest]] = defaultdict(list)
    for request in requests:
        index[request.address].append(request)
    return dict(index)


def _build_status_categories(
    requests: List[GraffitiServiceRequest],
) -> Dict[str, int]:
    """Assign deterministic integer codes to statuses (sorted alphabetically)."""
    unique_statuses = sorted({request.status for request in requests})
    return {status: code for code, status in enumerate(unique_statuses)}


EXPECTED_COLUMNS = [
    "borough",
    "days_since_last_tag",
    "total_tags",
    "response_time",
    "created_day_of_week",
    "created_month",
    "times_reported",
    "times_cleaned",
    "resolution_velocity",
    "latitude",
    "longitude",
    "status_code",
    "tagged_again",
    "cleaned",
    "time_to_next_update",
    "recurrence_window",
    "resolution_time",
    "index",
]


def extract_features(
    requests: List[GraffitiServiceRequest], cleaned_status_keywords: List[str]
) -> pandas.DataFrame:
    """Extract a feature DataFrame from service requests.

    Builds an address index and deterministic status codes before
    iterating, bringing overall complexity from O(n^3) down to O(n*k)
    where k is the max requests per address.
    """
    if not requests:
        return pandas.DataFrame(columns=EXPECTED_COLUMNS)

    status_categories = _build_status_categories(requests)
    address_index = _build_address_index(requests)

    feature_dicts = [
        request.to_feature_dict(
            status_categories, cleaned_status_keywords, address_index
        )
        for request in requests
    ]
    features = pandas.DataFrame(feature_dicts)
    features["borough"] = features["borough"].astype("category").cat.codes
    # Fill missing velocity with -1 (no prior history at address).
    # This is a feature column, so NaN would break the estimators.
    features["resolution_velocity"] = features["resolution_velocity"].fillna(-1)
    return features
