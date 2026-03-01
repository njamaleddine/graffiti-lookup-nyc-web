from unittest.mock import patch, Mock
from graffiti_data_pipeline.geocode.__main__ import main


class TestMain:
    @patch("graffiti_data_pipeline.geocode.__main__.geocode_service_requests")
    @patch("graffiti_data_pipeline.geocode.__main__.Geocoder")
    @patch("graffiti_data_pipeline.geocode.__main__.JsonFile")
    def test_loads_geocodes_and_saves(
        self, mock_jsonfile, mock_geocoder_cls, mock_geocode_svc
    ):
        lookups_store = Mock()
        cache_store = Mock()
        mock_jsonfile.side_effect = [lookups_store, cache_store]
        lookups_store.load.return_value = [{"address": "123 MAIN ST"}]
        cache_store.load.return_value = {}
        mock_geocode_svc.return_value = True
        geocoder = mock_geocoder_cls.from_config.return_value

        main()

        lookups_store.load.assert_called_once()
        mock_geocode_svc.assert_called_once_with(
            [{"address": "123 MAIN ST"}], geocoder
        )
        cache_store.save.assert_called_once_with(geocoder.cache)
        lookups_store.save.assert_called_once()

    @patch("graffiti_data_pipeline.geocode.__main__.geocode_service_requests")
    @patch("graffiti_data_pipeline.geocode.__main__.Geocoder")
    @patch("graffiti_data_pipeline.geocode.__main__.JsonFile")
    def test_skips_cache_save_when_nothing_geocoded(
        self, mock_jsonfile, mock_geocoder_cls, mock_geocode_svc
    ):
        lookups_store = Mock()
        cache_store = Mock()
        mock_jsonfile.side_effect = [lookups_store, cache_store]
        lookups_store.load.return_value = []
        cache_store.load.return_value = {}
        mock_geocode_svc.return_value = False

        main()

        cache_store.save.assert_not_called()
        lookups_store.save.assert_called_once()

    @patch("graffiti_data_pipeline.geocode.__main__.geocode_service_requests")
    @patch("graffiti_data_pipeline.geocode.__main__.Geocoder")
    @patch("graffiti_data_pipeline.geocode.__main__.JsonFile")
    def test_handles_empty_service_requests(
        self, mock_jsonfile, mock_geocoder_cls, mock_geocode_svc
    ):
        lookups_store = Mock()
        cache_store = Mock()
        mock_jsonfile.side_effect = [lookups_store, cache_store]
        lookups_store.load.return_value = []
        cache_store.load.return_value = {}
        mock_geocode_svc.return_value = False

        main()

        mock_geocode_svc.assert_called_once_with(
            [], mock_geocoder_cls.from_config.return_value
        )

    @patch("graffiti_data_pipeline.geocode.__main__.geocode_service_requests")
    @patch("graffiti_data_pipeline.geocode.__main__.Geocoder")
    @patch("graffiti_data_pipeline.geocode.__main__.JsonFile")
    def test_handles_geocoding_exception(
        self, mock_jsonfile, mock_geocoder_cls, mock_geocode_svc
    ):
        lookups_store = Mock()
        cache_store = Mock()
        mock_jsonfile.side_effect = [lookups_store, cache_store]
        lookups_store.load.return_value = [{"address": "123 MAIN ST"}]
        cache_store.load.return_value = {}
        mock_geocode_svc.side_effect = Exception("geocode error")

        # Should not raise — main() catches exceptions
        main()

        lookups_store.save.assert_not_called()

    @patch("graffiti_data_pipeline.geocode.__main__.geocode_service_requests")
    @patch("graffiti_data_pipeline.geocode.__main__.Geocoder")
    @patch("graffiti_data_pipeline.geocode.__main__.JsonFile")
    def test_handles_save_exception(
        self, mock_jsonfile, mock_geocoder_cls, mock_geocode_svc
    ):
        lookups_store = Mock()
        cache_store = Mock()
        mock_jsonfile.side_effect = [lookups_store, cache_store]
        lookups_store.load.return_value = [{"address": "123 MAIN ST"}]
        cache_store.load.return_value = {}
        mock_geocode_svc.return_value = True
        lookups_store.save.side_effect = Exception("save error")

        # Should not raise — main() catches exceptions
        main()
