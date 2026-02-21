"""
Feature Engineering for Graffiti Prediction

Provides functions to engineer features from graffiti service requests.
"""

from typing import List, Dict
import pandas

from graffiti_data_pipeline.prediction.request import GraffitiServiceRequest


def extract_features(
    requests: List[GraffitiServiceRequest], cleaned_status_keywords: List[str]
) -> pandas.DataFrame:
    status_categories: Dict[str, int] = {}
    feature_dicts = [
        req.to_feature_dict(status_categories, cleaned_status_keywords, requests)
        for req in requests
    ]
    features = pandas.DataFrame(feature_dicts)
    features["borough"] = features["borough"].astype("category").cat.codes
    return features
