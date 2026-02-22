import pytest
from graffiti_data_pipeline.prediction.features import extract_features
from graffiti_data_pipeline.prediction.request import GraffitiServiceRequest


class TestExtractFeatures:
    @pytest.fixture
    def sample_requests(self):
        record1 = {
            "address": "123 MAIN ST, Manhattan",
            "last_updated": "2026-02-01",
            "created": "2026-01-01",
            "status": "Site to be cleaned.",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "unique_key": "123-main-st",
        }
        record2 = {
            "address": "456 BROADWAY, Brooklyn",
            "last_updated": "2026-02-02",
            "created": "2026-01-02",
            "status": "Closed",
            "latitude": 40.6782,
            "longitude": -73.9442,
            "unique_key": "456-broadway",
        }
        return [GraffitiServiceRequest(record1), GraffitiServiceRequest(record2)]

    def test_extract_features_returns_dataframe(self, sample_requests):
        cleaned_status_keywords = ["cleaned"]
        features_dataframe = extract_features(sample_requests, cleaned_status_keywords)
        assert hasattr(features_dataframe, "columns")
        expected_columns = {
            "borough",
            "days_since_last_tag",
            "total_tags",
            "response_time",
            "latitude",
            "longitude",
            "status_code",
            "tagged_again",
            "cleaned",
            "time_to_next_update",
            "index",
        }
        assert expected_columns.issubset(set(features_dataframe.columns))

    def test_extract_features_empty_list(self):
        features_dataframe = extract_features([], ["cleaned"])
        expected_columns = {
            "borough",
            "days_since_last_tag",
            "total_tags",
            "response_time",
            "latitude",
            "longitude",
            "status_code",
            "tagged_again",
            "cleaned",
            "time_to_next_update",
            "index",
        }
        assert features_dataframe.empty
        assert expected_columns.issubset(set(features_dataframe.columns))

    def test_extract_features_missing_fields(self):
        incomplete_record = {"address": "789 UNKNOWN"}
        incomplete_request = GraffitiServiceRequest(incomplete_record)
        features_dataframe = extract_features([incomplete_request], ["cleaned"])
        expected_columns = {
            "borough",
            "days_since_last_tag",
            "total_tags",
            "response_time",
            "latitude",
            "longitude",
            "status_code",
            "tagged_again",
            "cleaned",
            "time_to_next_update",
            "index",
        }
        assert expected_columns.issubset(set(features_dataframe.columns))
        assert features_dataframe.shape[0] == 1

    def test_extract_features_invalid_type(self):
        with pytest.raises(Exception):
            extract_features([123], ["cleaned"])
