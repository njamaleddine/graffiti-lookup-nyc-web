from datetime import datetime
from unittest.mock import patch
from graffiti_data_pipeline.filter_service_requests import (
    was_recently_updated,
    get_active_service_requests,
)
from graffiti_data_pipeline.config import GRAFFITI_COMPLETE_STATUSES


class TestWasRecentlyUpdated:
    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_recent_date_returns_true(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)

        assert was_recently_updated("2026-02-04", days=2)

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_today_returns_true(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)
        today = "2026-02-05"

        assert was_recently_updated(today, days=1)

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_future_date_returns_true(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)

        assert was_recently_updated("2026-02-10", days=2)

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_leap_year_date(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)

        assert was_recently_updated("2024-02-29", days=1000)

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_old_date_returns_false(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)

        assert not was_recently_updated("2020-01-01", days=2)

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_invalid_date_returns_false(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)

        assert not was_recently_updated("invalid-date", days=2)

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_empty_string_returns_false(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)

        assert not was_recently_updated("", days=2)

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_none_returns_false(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)

        assert not was_recently_updated(None, days=2)

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_custom_days(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)

        assert was_recently_updated("2026-02-01", days=5)


class TestGetActiveServiceRequests:
    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_filters_active_requests(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)
        requests = [
            {"status": "OPEN", "last_updated": "2026-02-04"},
            {"status": "CityOwnedIneligible", "last_updated": "2026-02-04"},
            {
                "status": "Cleaning crew dispatched.  Property cleaned.",
                "last_updated": "2026-02-04",
            },
            {"status": "OPEN", "last_updated": "2020-01-01"},
            {"status": "Graffiti is intentional.", "last_updated": "2026-02-04"},
            {"status": "OPEN", "last_updated": "invalid-date"},
        ]
        expected = [{"status": "OPEN", "last_updated": "2026-02-04"}]
        active = get_active_service_requests(requests, days=2)

        assert active == expected

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_missing_last_updated(self, mock_datetime):
        mock_datetime.now.return_value = mock_datetime.strptime(
            "2026-02-05", "%Y-%m-%d"
        )
        requests = [
            {"status": "OPEN"},
            {"status": "OPEN", "last_updated": None},
        ]

        assert get_active_service_requests(requests, days=2) == []

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_missing_status(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)
        requests = [
            {"last_updated": "2026-02-04"},
            {"last_updated": "2020-01-01"},
        ]
        expected = [{"last_updated": "2026-02-04"}]
        assert get_active_service_requests(requests, days=2) == expected

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_irrelevant_fields(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)
        requests = [
            {"status": "OPEN", "last_updated": "2026-02-04", "foo": "bar"},
        ]
        expected = [{"status": "OPEN", "last_updated": "2026-02-04", "foo": "bar"}]
        assert get_active_service_requests(requests, days=2) == expected

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_empty_list_returns_empty(self, mock_datetime):
        mock_datetime.now.return_value = mock_datetime.strptime(
            "2026-02-05", "%Y-%m-%d"
        )

        assert get_active_service_requests([], days=2) == []

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_all_complete_statuses_filtered(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        requests = [
            {"status": status, "last_updated": "2026-02-04"}
            for status in GRAFFITI_COMPLETE_STATUSES
        ]

        assert get_active_service_requests(requests, days=2) == []

    @patch("graffiti_data_pipeline.filter_service_requests.datetime")
    def test_all_recent_and_open(self, mock_datetime):
        mock_datetime.now.return_value = datetime.strptime("2026-02-05", "%Y-%m-%d")
        mock_datetime.strptime.side_effect = lambda s, fmt: datetime.strptime(s, fmt)
        requests = [
            {"status": "OPEN", "last_updated": "2026-02-04"},
            {"status": "OPEN", "last_updated": "2026-02-05"},
        ]
        expected = [
            {"status": "OPEN", "last_updated": "2026-02-04"},
            {"status": "OPEN", "last_updated": "2026-02-05"},
        ]
        active = get_active_service_requests(requests, days=2)

        assert active == expected
