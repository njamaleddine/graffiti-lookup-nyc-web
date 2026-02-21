import pytest
from unittest.mock import Mock, patch
from graffiti_data_pipeline.geocoder import geocode_address, geocode_addresses
from geopy.exc import GeocoderTimedOut


class TestGeocodeAddress:
    def test_empty_service_requests(self):
        cache = {}
        geocode_fn = Mock()

        result = geocode_address("", geocode_fn, cache)

        assert result == (None, None)

    def test_malformed_service_requests(self):
        cache = {}
        geocode_fn = Mock()

        result = geocode_address(None, geocode_fn, cache)

        assert result == (None, None)

        result = geocode_address(123, geocode_fn, cache)

        assert result == (None, None)

    def test_geocoder_exception(self):
        cache = {}

        def raise_timeout(address):
            raise GeocoderTimedOut("timeout")

        geocode_fn = Mock()
        geocode_fn.side_effect = raise_timeout

        # geocode_fn itself should raise
        with pytest.raises(Exception):
            geocode_fn("123 MAIN ST")

        # geocode_address should handle the exception and return (None, None)
        result = geocode_address("123 MAIN ST", geocode_fn, cache)
        assert result == (None, None)

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
    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.JsonFile")
    def test_empty_service_requests(
        self, mock_jsonfile, mock_rate_limiter, mock_nominatim
    ):
        mock_cache = {}
        mock_jsonfile.return_value.load.return_value = mock_cache
        mock_jsonfile.return_value.save = Mock()
        service_requests = []

        result = geocode_addresses(
            service_requests,
            cache_file="fake_geocode_cache.json",
            min_delay_seconds=0,
            error_wait_seconds=0,
        )

        assert result == []
        mock_jsonfile.return_value.save.assert_not_called()

    @patch("geocode.geocoder.Nominatim")
    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.JsonFile")
    def test_malformed_service_requests(
        self, mock_jsonfile, mock_rate_limiter, mock_nominatim
    ):
        mock_cache = {}
        mock_jsonfile.return_value.load.return_value = mock_cache
        mock_jsonfile.return_value.save = Mock()
        service_requests = [{}, {"foo": "bar"}, {"address": None}]

        result = geocode_addresses(
            service_requests,
            cache_file="fake_geocode_cache.json",
            min_delay_seconds=0,
            error_wait_seconds=0,
        )

        # Should not add latitude/longitude to malformed requests
        for r in result:
            assert "latitude" not in r and "longitude" not in r
        mock_jsonfile.return_value.save.assert_not_called()

    @patch("geocode.geocoder.JsonFile")
    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.Nominatim")
    def test_multiple_addresses(self, mock_nominatim, mock_rate_limiter, mock_jsonfile):
        mock_cache = {}
        mock_jsonfile.return_value.load.return_value = mock_cache
        mock_jsonfile.return_value.save = Mock()
        mock_rate_limiter.return_value.return_value.latitude = 40.7128
        mock_rate_limiter.return_value.return_value.longitude = -74.0060
        service_requests = [
            {"address": "123 MAIN ST"},
            {"address": "456 BROADWAY"},
            {"address": "123 MAIN ST"},
        ]

        result = geocode_addresses(
            service_requests,
            cache_file="fake_geocode_cache.json",
            min_delay_seconds=0,
            error_wait_seconds=0,
        )

        assert result[0]["latitude"] == 40.7128
        assert result[0]["longitude"] == -74.0060
        assert result[2]["latitude"] == 40.7128
        assert result[2]["longitude"] == -74.0060

    @patch("geocode.geocoder.Nominatim")
    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.JsonFile")
    def test_cache_load_exception(
        self, mock_jsonfile, mock_rate_limiter, mock_nominatim
    ):
        mock_jsonfile.return_value.load.side_effect = Exception("load error")
        mock_jsonfile.return_value.save = Mock()
        service_requests = [{"address": "123 MAIN ST"}]

        with pytest.raises(Exception):
            geocode_addresses(
                service_requests,
                cache_file="fake_geocode_cache.json",
                min_delay_seconds=0,
                error_wait_seconds=0,
            )

        mock_jsonfile.return_value.save.assert_not_called()

    @patch("geocode.geocoder.Nominatim")
    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.JsonFile")
    def test_cache_save_exception(
        self, mock_jsonfile, mock_rate_limiter, mock_nominatim
    ):
        mock_cache = {}
        mock_jsonfile.return_value.load.return_value = mock_cache
        mock_jsonfile.return_value.save.side_effect = Exception("save error")
        service_requests = [{"address": "123 MAIN ST"}]

        with pytest.raises(Exception):
            geocode_addresses(
                service_requests,
                cache_file="fake_geocode_cache.json",
                min_delay_seconds=0,
                error_wait_seconds=0,
            )

    @patch("geocode.geocoder.JsonFile")
    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.Nominatim")
    def test_cache_save_called_when_address_geocoded(
        self, mock_nominatim, mock_rate_limiter, mock_jsonfile
    ):
        mock_cache = {}
        mock_jsonfile.return_value.load.return_value = mock_cache
        mock_jsonfile.return_value.save = Mock()
        mock_rate_limiter.return_value.return_value.latitude = 40.7128
        mock_rate_limiter.return_value.return_value.longitude = -74.0060
        service_requests = [{"address": "123 MAIN ST"}]

        geocode_addresses(
            service_requests,
            cache_file="fake_geocode_cache.json",
            min_delay_seconds=0,
            error_wait_seconds=0,
        )

        mock_jsonfile.return_value.save.assert_called_once_with(mock_cache)

    @patch("geocode.geocoder.Nominatim")
    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.JsonFile")
    def test_cache_save_not_called_when_no_address_geocoded(
        self, mock_jsonfile, mock_rate_limiter, mock_nominatim
    ):
        mock_cache = {}
        mock_jsonfile.return_value.load.return_value = mock_cache
        mock_jsonfile.return_value.save = Mock()
        service_requests = [
            {"address": "123 MAIN ST", "latitude": 40.7128, "longitude": -74.0060}
        ]

        geocode_addresses(
            service_requests,
            cache_file="fake_geocode_cache.json",
            min_delay_seconds=0,
            error_wait_seconds=0,
        )

        mock_jsonfile.return_value.save.assert_not_called()

    @patch("geocode.geocoder.JsonFile")
    @patch("geocode.geocoder.Nominatim")
    def test_skips_service_requests_that_already_have_coordinates(
        self, mock_nominatim, mock_jsonfile
    ):
        mock_cache = {}
        mock_jsonfile.return_value.load.return_value = mock_cache
        mock_jsonfile.return_value.save = Mock()
        service_requests = [
            {"address": "123 MAIN ST", "latitude": 40.7128, "longitude": -74.0060}
        ]

        result = geocode_addresses(
            service_requests,
            cache_file="fake_geocode_cache.json",
            min_delay_seconds=0,
            error_wait_seconds=0,
        )

        assert result[0]["latitude"] == 40.7128
        assert result[0]["longitude"] == -74.0060

    @patch("geocode.geocoder.JsonFile")
    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.Nominatim")
    def test_geocodes_service_requests_missing_coordinates(
        self, mock_nominatim, mock_rate_limiter, mock_jsonfile
    ):
        mock_cache = {}
        mock_jsonfile.return_value.load.return_value = mock_cache
        mock_jsonfile.return_value.save = Mock()
        service_requests = [{"address": "123 MAIN ST"}]

        mock_rate_limiter.return_value.return_value.latitude = 40.7128
        mock_rate_limiter.return_value.return_value.longitude = -74.0060

        result = geocode_addresses(
            service_requests,
            cache_file="fake_geocode_cache.json",
            min_delay_seconds=0,
            error_wait_seconds=0,
        )

        assert result[0]["latitude"] == 40.7128
        assert result[0]["longitude"] == -74.0060

    @patch("geocode.geocoder.JsonFile")
    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.Nominatim")
    def test_uses_cached_coordinates_instead_of_calling_geocoder(
        self, mock_nominatim, mock_rate_limiter, mock_jsonfile
    ):
        mock_cache = {"123 MAIN ST": [40.7128, -74.0060]}
        mock_jsonfile.return_value.load.return_value = mock_cache
        mock_jsonfile.return_value.save = Mock()
        service_requests = [{"address": "123 MAIN ST"}]

        mock_rate_limiter.return_value.return_value = None

        result = geocode_addresses(
            service_requests,
            cache_file="fake_geocode_cache.json",
            min_delay_seconds=0,
            error_wait_seconds=0,
        )

        assert result[0]["latitude"] == 40.7128
        assert result[0]["longitude"] == -74.0060

    @patch("geocode.geocoder.JsonFile")
    @patch("geocode.geocoder.RateLimiter")
    @patch("geocode.geocoder.Nominatim")
    def test_saves_newly_geocoded_addresses_to_cache_file(
        self, mock_nominatim, mock_rate_limiter, mock_jsonfile
    ):
        mock_cache = {}
        mock_jsonfile.return_value.load.return_value = mock_cache
        mock_jsonfile.return_value.save = Mock()
        service_requests = [{"address": "123 MAIN ST"}]

        mock_rate_limiter.return_value.return_value.latitude = 40.7128
        mock_rate_limiter.return_value.return_value.longitude = -74.0060

        geocode_addresses(
            service_requests,
            cache_file="fake_geocode_cache.json",
            min_delay_seconds=0,
            error_wait_seconds=0,
        )

        mock_jsonfile.return_value.save.assert_called_once_with(mock_cache)
