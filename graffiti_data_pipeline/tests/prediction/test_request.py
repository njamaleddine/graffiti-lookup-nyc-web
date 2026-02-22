import pytest
import pandas
from graffiti_data_pipeline.prediction.request import GraffitiServiceRequest


class TestGraffitiServiceRequest:
    @pytest.fixture
    def sample_record(self):
        return {
            "address": "123 MAIN ST, Manhattan",
            "last_updated": "2026-02-01",
            "created": "2026-01-01",
            "status": "Site to be cleaned.",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "unique_key": "123-main-st",
        }

    @pytest.fixture
    def sample_requests(self, sample_record):
        return [
            GraffitiServiceRequest(sample_record),
            GraffitiServiceRequest(sample_record),
        ]

    def test_get_borough(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        assert request.get_borough() == "manhattan"

    def test_get_last_tag_date(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        assert isinstance(request.get_last_tag_date(), pandas.Timestamp)

    def test_get_created_tag_date(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        assert isinstance(request.get_created_tag_date(), pandas.Timestamp)

    def test_get_days_since_last_tag(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        assert isinstance(request.get_days_since_last_tag(), int)

    def test_get_response_time_days(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        assert isinstance(request.get_response_time_days(), int)

    def test_get_tag_count_at_location(self, sample_requests):
        request = sample_requests[0]
        assert request.get_tag_count_at_location(sample_requests) == 2

    def test_get_tagged_again(self, sample_requests):
        request = sample_requests[0]
        assert request.get_tagged_again(sample_requests) == 1

    def test_get_status_code(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        status_categories = {}
        code = request.get_status_code(status_categories)
        assert isinstance(code, int)
        assert sample_record["status"] in status_categories

    def test_is_cleaned(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        cleaned_keywords = ["cleaned"]
        assert request.is_cleaned(cleaned_keywords) == 1

    def test_get_time_to_next_update(self, sample_requests):
        request = sample_requests[0]
        value = request.get_time_to_next_update(sample_requests)
        assert value is None or isinstance(value, int)

    def test_to_feature_dict(self, sample_requests):
        request = sample_requests[0]
        status_categories = {}
        cleaned_keywords = ["cleaned"]
        features = request.to_feature_dict(
            status_categories, cleaned_keywords, sample_requests
        )
        expected_keys = {
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
        assert isinstance(features, dict)
        assert expected_keys.issubset(set(features.keys()))

    def test_missing_fields(self):
        incomplete_record = {"address": "789 UNKNOWN"}
        request = GraffitiServiceRequest(incomplete_record)
        assert request.get_borough() == "unknown"
        assert isinstance(request.get_last_tag_date(), pandas.Timestamp)
        assert isinstance(request.get_created_tag_date(), pandas.Timestamp)
        assert isinstance(request.get_days_since_last_tag(), int)
        assert isinstance(request.get_response_time_days(), int)
        status_categories = {}
        assert isinstance(request.get_status_code(status_categories), int)
        cleaned_keywords = ["cleaned"]
        assert request.is_cleaned(cleaned_keywords) == 0
        assert request.get_tag_count_at_location([]) == 0
        assert request.get_tagged_again([]) == 0
        assert request.get_time_to_next_update([]) is None
        features = request.to_feature_dict(status_categories, cleaned_keywords, [])
        assert isinstance(features, dict)
        assert "borough" in features
        assert "index" in features

    def test_invalid_type(self):
        with pytest.raises(Exception):
            GraffitiServiceRequest(123)

    def test_empty_request_list(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        assert request.get_tag_count_at_location([]) == 0
        assert request.get_tagged_again([]) == 0
        assert request.get_time_to_next_update([]) is None
