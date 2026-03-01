from unittest.mock import Mock
from geopy.exc import GeocoderTimedOut

from graffiti_data_pipeline.geocode.geocoder import (
    Coordinates,
    Geocoder,
    geocode_service_requests,
)


class TestGeocoderGeocode:
    def test_returns_none_for_empty_string(self):
        geocoder = Geocoder(Mock())

        assert geocoder.geocode("") is None

    def test_returns_none_for_non_string_input(self):
        geocoder = Geocoder(Mock())

        assert geocoder.geocode(None) is None
        assert geocoder.geocode(123) is None

    def test_returns_cached_coordinates_without_calling_service(self):
        geocode_fn = Mock()
        cache = {"123 MAIN ST": (40.7128, -74.0060)}
        geocoder = Geocoder(geocode_fn, cache)

        result = geocoder.geocode("123 MAIN ST")

        assert result == Coordinates(40.7128, -74.0060)
        geocode_fn.assert_not_called()

    def test_queries_service_and_caches_result_on_miss(self):
        location = Mock(latitude=40.7128, longitude=-74.0060)
        geocode_fn = Mock(return_value=location)
        geocoder = Geocoder(geocode_fn)

        result = geocoder.geocode("123 MAIN ST")

        assert result == Coordinates(40.7128, -74.0060)
        assert geocoder.cache["123 MAIN ST"] == (40.7128, -74.0060)

    def test_returns_none_when_service_finds_no_result(self):
        geocode_fn = Mock(return_value=None)
        geocoder = Geocoder(geocode_fn)

        assert geocoder.geocode("UNKNOWN ADDRESS") is None
        assert "UNKNOWN ADDRESS" not in geocoder.cache

    def test_returns_none_on_geocoder_timeout(self):
        geocode_fn = Mock(side_effect=GeocoderTimedOut("timeout"))
        geocoder = Geocoder(geocode_fn)

        assert geocoder.geocode("123 MAIN ST") is None

    def test_normalizes_numbered_street_names_before_geocoding(self):
        location = Mock(latitude=40.7128, longitude=-74.0060)
        geocode_fn = Mock(return_value=location)
        geocoder = Geocoder(geocode_fn)

        geocoder.geocode("3 STREET")

        call_args = geocode_fn.call_args[0][0]
        assert "3RD STREET" in call_args


class TestGeocodeServiceRequests:
    def test_returns_false_for_empty_list(self):
        geocoder = Geocoder(Mock())

        assert geocode_service_requests([], geocoder) is False

    def test_skips_malformed_requests(self):
        geocoder = Geocoder(Mock())
        requests = [{}, {"foo": "bar"}, {"address": None}]

        assert geocode_service_requests(requests, geocoder) is False
        for r in requests:
            assert "latitude" not in r
            assert "longitude" not in r

    def test_geocodes_multiple_addresses(self):
        location = Mock(latitude=40.7128, longitude=-74.0060)
        geocode_fn = Mock(return_value=location)
        geocoder = Geocoder(geocode_fn)
        requests = [
            {"address": "123 MAIN ST"},
            {"address": "456 BROADWAY"},
        ]

        result = geocode_service_requests(requests, geocoder)

        assert result is True
        assert requests[0]["latitude"] == 40.7128
        assert requests[1]["longitude"] == -74.0060

    def test_skips_geocoding_when_coordinates_exist(self):
        geocode_fn = Mock()
        geocoder = Geocoder(geocode_fn, cache={
            "123 MAIN ST": [40.7128, -74.0060],
        })
        requests = [
            {"address": "123 MAIN ST", "latitude": 40.7128, "longitude": -74.0060}
        ]

        result = geocode_service_requests(requests, geocoder)

        assert result is False
        geocode_fn.assert_not_called()

    def test_returns_true_when_new_coordinates_resolved(self):
        location = Mock(latitude=40.7128, longitude=-74.0060)
        geocode_fn = Mock(return_value=location)
        geocoder = Geocoder(geocode_fn)
        requests = [{"address": "123 MAIN ST"}]

        assert geocode_service_requests(requests, geocoder) is True

    def test_returns_false_when_no_coordinates_resolved(self):
        geocode_fn = Mock(return_value=None)
        geocoder = Geocoder(geocode_fn)
        requests = [{"address": "UNKNOWN"}]

        assert geocode_service_requests(requests, geocoder) is False

    def test_uses_cached_coordinates(self):
        geocode_fn = Mock()
        cache = {"123 MAIN ST": (40.7128, -74.0060)}
        geocoder = Geocoder(geocode_fn, cache)
        requests = [{"address": "123 MAIN ST"}]

        geocode_service_requests(requests, geocoder)

        assert requests[0]["latitude"] == 40.7128
        assert requests[0]["longitude"] == -74.0060
        geocode_fn.assert_not_called()

    def test_backfills_cache_from_existing_coordinates(self):
        geocode_fn = Mock()
        geocoder = Geocoder(geocode_fn, cache={})
        requests = [
            {
                "address": "123 MAIN ST",
                "latitude": 40.7128,
                "longitude": -74.0060,
            }
        ]

        result = geocode_service_requests(requests, geocoder)

        assert result is True
        assert geocoder.cache["123 MAIN ST"] == (40.7128, -74.0060)
        geocode_fn.assert_not_called()

    def test_does_not_backfill_when_cache_already_has_address(self):
        geocode_fn = Mock()
        existing_coords = (40.0, -73.0)
        cache = {"123 MAIN ST": existing_coords}
        geocoder = Geocoder(geocode_fn, cache)
        requests = [
            {
                "address": "123 MAIN ST",
                "latitude": 40.7128,
                "longitude": -74.0060,
            }
        ]

        result = geocode_service_requests(requests, geocoder)

        assert result is False
        assert geocoder.cache["123 MAIN ST"] == existing_coords
