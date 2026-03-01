import pytest
import pandas
from graffiti_data_pipeline.config import GRAFFITI_COMPLETE_STATUSES
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
        address_index = {"123 MAIN ST, Manhattan": sample_requests}
        assert request.get_tag_count_at_location(address_index) == 2

    def test_get_tagged_again(self, sample_requests):
        request = sample_requests[0]
        address_index = {"123 MAIN ST, Manhattan": sample_requests}
        assert request.get_tagged_again(address_index) == 1

    def test_get_status_code(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        status_categories = {}
        code = request.get_status_code(status_categories)
        assert isinstance(code, int)
        assert sample_record["status"] in status_categories

    def test_is_cleaned_matches_keyword_substring(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        assert request.is_cleaned(["cleaned"]) == 1

    def test_pending_cleanup_is_not_cleaned(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        production_keyword = "Cleaning crew dispatched.  Property cleaned."
        assert request.is_cleaned([production_keyword]) == 0

    def test_is_cleaned_with_actual_cleaned_status(self):
        record = {
            "address": "123 MAIN ST, Manhattan",
            "status": "Cleaning crew dispatched.  Property cleaned.",
        }
        request = GraffitiServiceRequest(record)
        assert request.is_cleaned(
            ["Cleaning crew dispatched.  Property cleaned."]
        ) == 1

    def test_get_time_to_next_update(self, sample_requests):
        request = sample_requests[0]
        address_index = {"123 MAIN ST, Manhattan": sample_requests}
        value = request.get_time_to_next_update(address_index)
        assert value is None or isinstance(value, int)

    def test_to_feature_dict(self, sample_requests):
        request = sample_requests[0]
        status_categories = {}
        cleaned_keywords = ["cleaned"]
        address_index = {"123 MAIN ST, Manhattan": sample_requests}
        features = request.to_feature_dict(
            status_categories, cleaned_keywords, address_index
        )
        expected_keys = {
            "borough",
            "days_since_last_tag",
            "total_tags",
            "response_time",
            "created_day_of_week",
            "created_month",
            "cleaning_cycle_count",
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
        assert request.get_tag_count_at_location({}) == 0
        assert request.get_tagged_again({}) == 0
        assert request.get_time_to_next_update({}) is None
        features = request.to_feature_dict(status_categories, cleaned_keywords, {})
        assert isinstance(features, dict)
        assert "borough" in features
        assert "index" in features

    def test_invalid_type(self):
        with pytest.raises(Exception):
            GraffitiServiceRequest(123)

    def test_empty_request_list(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        assert request.get_tag_count_at_location({}) == 0
        assert request.get_tagged_again({}) == 0
        assert request.get_time_to_next_update({}) is None

    def test_get_created_day_of_week(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        day = request.get_created_day_of_week()
        # 2026-01-01 is a Thursday (dayofweek=3)
        assert day == 3

    def test_get_created_month(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        assert request.get_created_month() == 1

    def test_cleaning_cycle_count_with_complete_status(self):
        complete_status = GRAFFITI_COMPLETE_STATUSES[0]
        records = [
            {
                "address": "10 ELM ST, Bronx",
                "created": "2026-01-01",
                "last_updated": "2026-01-15",
                "status": complete_status,
            },
            {
                "address": "10 ELM ST, Bronx",
                "created": "2026-02-01",
                "last_updated": "2026-02-10",
                "status": "Open",
            },
        ]
        requests = [GraffitiServiceRequest(r) for r in records]
        address_index = {"10 ELM ST, Bronx": requests}
        # The completed request (Jan 15) is followed by a new report (Feb 1)
        # so there is 1 full report→clean→report cycle.
        assert requests[1].get_cleaning_cycle_count(address_index) == 1

    def test_cleaning_cycle_count_no_completions(self, sample_requests):
        address_index = {"123 MAIN ST, Manhattan": sample_requests}
        # "Site to be cleaned." is NOT in GRAFFITI_COMPLETE_STATUSES
        assert sample_requests[0].get_cleaning_cycle_count(address_index) == 0

    def test_cleaning_cycle_count_completed_without_followup(self):
        """A completed request with no subsequent report = 0 cycles."""
        complete_status = GRAFFITI_COMPLETE_STATUSES[0]
        records = [
            {
                "address": "10 ELM ST, Bronx",
                "created": "2026-01-01",
                "last_updated": "2026-01-15",
                "status": complete_status,
            },
        ]
        requests = [GraffitiServiceRequest(r) for r in records]
        address_index = {"10 ELM ST, Bronx": requests}
        assert requests[0].get_cleaning_cycle_count(address_index) == 0

    def test_cleaning_cycle_count_multiple_cycles(self):
        """Two clean→re-report cycles should return 2."""
        complete_status = GRAFFITI_COMPLETE_STATUSES[0]
        records = [
            {
                "address": "10 ELM ST, Bronx",
                "created": "2026-01-01",
                "last_updated": "2026-01-15",
                "status": complete_status,
            },
            {
                "address": "10 ELM ST, Bronx",
                "created": "2026-02-01",
                "last_updated": "2026-02-20",
                "status": complete_status,
            },
            {
                "address": "10 ELM ST, Bronx",
                "created": "2026-03-01",
                "last_updated": "2026-03-05",
                "status": "Open",
            },
        ]
        requests = [GraffitiServiceRequest(r) for r in records]
        address_index = {"10 ELM ST, Bronx": requests}
        # Both completed requests are followed by later reports
        assert requests[2].get_cleaning_cycle_count(address_index) == 2

    def test_recurrence_window_returns_days(self):
        records = [
            {
                "address": "5 OAK AVE, Brooklyn",
                "created": "2026-01-01",
                "last_updated": "2026-01-05",
                "status": "Open",
            },
            {
                "address": "5 OAK AVE, Brooklyn",
                "created": "2026-01-11",
                "last_updated": "2026-01-15",
                "status": "Open",
            },
        ]
        requests = [GraffitiServiceRequest(r) for r in records]
        address_index = {"5 OAK AVE, Brooklyn": requests}
        assert requests[0].get_recurrence_window(address_index) == 10

    def test_recurrence_window_none_when_no_later_report(self, sample_record):
        request = GraffitiServiceRequest(sample_record)
        address_index = {"123 MAIN ST, Manhattan": [request]}
        assert request.get_recurrence_window(address_index) is None

    def test_resolution_time_returns_days(self):
        complete_status = GRAFFITI_COMPLETE_STATUSES[0]
        records = [
            {
                "address": "7 PINE RD, Queens",
                "created": "2026-01-01",
                "last_updated": "2026-01-03",
                "status": "Open",
            },
            {
                "address": "7 PINE RD, Queens",
                "created": "2026-01-02",
                "last_updated": "2026-01-21",
                "status": complete_status,
            },
        ]
        requests = [GraffitiServiceRequest(r) for r in records]
        address_index = {"7 PINE RD, Queens": requests}
        # Created 2026-01-01, completed req last_updated 2026-01-21 → 20 days
        assert requests[0].get_resolution_time(address_index) == 20

    def test_resolution_time_none_when_no_completion(self, sample_requests):
        address_index = {"123 MAIN ST, Manhattan": sample_requests}
        assert sample_requests[0].get_resolution_time(address_index) is None

    def test_resolution_velocity_returns_average_days(self):
        """Velocity = average resolution time of past completed requests."""
        complete_status = GRAFFITI_COMPLETE_STATUSES[0]
        records = [
            {
                "address": "8 ASH LN, Bronx",
                "created": "2026-01-01",
                "last_updated": "2026-01-11",  # 10 days
                "status": complete_status,
            },
            {
                "address": "8 ASH LN, Bronx",
                "created": "2026-01-05",
                "last_updated": "2026-01-25",  # 20 days
                "status": complete_status,
            },
            {
                "address": "8 ASH LN, Bronx",
                "created": "2026-02-01",
                "last_updated": "2026-02-05",
                "status": "Open",
            },
        ]
        requests = [GraffitiServiceRequest(r) for r in records]
        address_index = {"8 ASH LN, Bronx": requests}
        # For the third request (created Feb 1), past completed = first two
        # Average = (10 + 20) / 2 = 15
        assert requests[2].get_resolution_velocity(address_index) == 15

    def test_resolution_velocity_none_when_no_history(self, sample_requests):
        address_index = {"123 MAIN ST, Manhattan": sample_requests}
        assert sample_requests[0].get_resolution_velocity(address_index) is None

    def test_resolution_velocity_excludes_future_completions(self):
        """Only past completions (before this request's created) count."""
        complete_status = GRAFFITI_COMPLETE_STATUSES[0]
        records = [
            {
                "address": "8 ASH LN, Bronx",
                "created": "2026-01-01",
                "last_updated": "2026-01-05",
                "status": "Open",
            },
            {
                "address": "8 ASH LN, Bronx",
                "created": "2026-01-10",
                "last_updated": "2026-01-20",
                "status": complete_status,
            },
        ]
        requests = [GraffitiServiceRequest(r) for r in records]
        address_index = {"8 ASH LN, Bronx": requests}
        # First request created Jan 1; the only completion is Jan 20 (after Jan 1)
        # so there's no *past* history → None
        assert requests[0].get_resolution_velocity(address_index) is None
