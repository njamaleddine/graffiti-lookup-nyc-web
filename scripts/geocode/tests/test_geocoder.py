import json
from unittest.mock import Mock, patch

from geocode.geocoder import (
    geocode_address,
    geocode_addresses,
    load_geocode_cache,
    save_geocode_cache,
)


class TestLoadGeocodeCache:
    def test_returns_cache_data_when_file_exists(self, tmp_path):
        cache_file = tmp_path / "cache.json"
        cache_data = {"123 MAIN ST": [40.7128, -74.0060]}
        cache_file.write_text(json.dumps(cache_data))

        result = load_geocode_cache(str(cache_file))

        assert result == cache_data

    def test_returns_empty_dict_when_file_does_not_exist(self, tmp_path):
        cache_file = tmp_path / "nonexistent.json"

        result = load_geocode_cache(str(cache_file))

        assert result == {}


class TestSaveGeocodeCache:
    def test_writes_cache_data_to_json_file(self, tmp_path):
        cache_file = tmp_path / "cache.json"
        cache_data = {"123 MAIN ST": [40.7128, -74.0060]}

        save_geocode_cache(cache_data, str(cache_file))

        with open(cache_file) as f:
            saved = json.load(f)
        assert saved == cache_data


class TestGeocodeAddress:
    def test_returns_cached_coordinates_without_calling_geocoder(self):
        cache = {"123 MAIN ST": (40.7128, -74.0060)}
        geocode_fn = Mock()

        result = geocode_address("123 MAIN ST", geocode_fn, cache)

        assert result == (40.7128, -74.0060)
        geocode_fn.assert_not_called()

    def test_calls_geocoder_and_caches_result_on_cache_miss(self):
        cache = {}
        mock_location = Mock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060
        geocode_fn = Mock(return_value=mock_location)

        result = geocode_address("123 MAIN ST", geocode_fn, cache)

        assert result == (40.7128, -74.0060)
        assert cache["123 MAIN ST"] == (40.7128, -74.0060)

    def test_returns_none_tuple_when_geocoder_finds_no_result(self):
        cache = {}
        geocode_fn = Mock(return_value=None)

        result = geocode_address("UNKNOWN ADDRESS", geocode_fn, cache)

        assert result == (None, None)
        assert "UNKNOWN ADDRESS" not in cache

    def test_normalizes_numbered_street_names_before_geocoding(self):
        cache = {}
        mock_location = Mock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060
        geocode_fn = Mock(return_value=mock_location)

        geocode_address("3 STREET", geocode_fn, cache)

        call_args = geocode_fn.call_args[0][0]
        assert "3RD STREET" in call_args


class TestGeocodeAddresses:
    @patch("geocode.geocoder.Nominatim")
    def test_skips_service_requests_that_already_have_coordinates(
        self, mock_nominatim, tmp_path
    ):
        cache_file = tmp_path / "cache.json"
        cache_file.write_text("{}")

        service_requests = [
            {"address": "123 MAIN ST", "latitude": 40.7128, "longitude": -74.0060}
        ]

        result = geocode_addresses(service_requests, cache_file=str(cache_file))

        assert result[0]["latitude"] == 40.7128
        assert result[0]["longitude"] == -74.0060

    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.Nominatim")
    def test_geocodes_service_requests_missing_coordinates(
        self, mock_nominatim, mock_rate_limiter, tmp_path
    ):
        cache_file = tmp_path / "cache.json"
        cache_file.write_text("{}")

        service_requests = [{"address": "123 MAIN ST"}]

        mock_rate_limiter.return_value.return_value.latitude = 40.7128
        mock_rate_limiter.return_value.return_value.longitude = -74.0060

        result = geocode_addresses(service_requests, cache_file=str(cache_file))

        assert result[0]["latitude"] == 40.7128
        assert result[0]["longitude"] == -74.0060

    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.Nominatim")
    def test_uses_cached_coordinates_instead_of_calling_geocoder(
        self, mock_nominatim, mock_rate_limiter, tmp_path
    ):
        cache_file = tmp_path / "cache.json"
        cache_data = {"123 MAIN ST": [40.7128, -74.0060]}
        cache_file.write_text(json.dumps(cache_data))

        service_requests = [{"address": "123 MAIN ST"}]

        mock_rate_limiter.return_value.return_value = None

        result = geocode_addresses(service_requests, cache_file=str(cache_file))

        assert result[0]["latitude"] == 40.7128
        assert result[0]["longitude"] == -74.0060

    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.Nominatim")
    def test_saves_newly_geocoded_addresses_to_cache_file(
        self, mock_nominatim, mock_rate_limiter, tmp_path
    ):
        cache_file = tmp_path / "cache.json"
        cache_file.write_text("{}")

        service_requests = [{"address": "123 MAIN ST"}]

        mock_rate_limiter.return_value.return_value.latitude = 40.7128
        mock_rate_limiter.return_value.return_value.longitude = -74.0060

        geocode_addresses(service_requests, cache_file=str(cache_file))

        with open(cache_file) as f:
            saved_cache = json.load(f)
        assert "123 MAIN ST" in saved_cache
