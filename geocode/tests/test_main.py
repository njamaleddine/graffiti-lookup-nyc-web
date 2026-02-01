import json
from unittest.mock import patch

import pytest
from geocode.__main__ import load_service_requests, save_service_requests, main


class TestLoadServiceRequests:
    def test_returns_parsed_json_data_from_file(self, tmp_path):
        data_file = tmp_path / "data.json"
        data = [{"address": "123 MAIN ST", "id": 1}]
        data_file.write_text(json.dumps(data))

        result = load_service_requests(str(data_file))

        assert result == data

    def test_raises_file_not_found_error_when_file_does_not_exist(self, tmp_path):
        data_file = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            load_service_requests(str(data_file))


class TestSaveServiceRequests:
    def test_writes_service_requests_to_json_file(self, tmp_path):
        data_file = tmp_path / "data.json"
        data = [{"address": "123 MAIN ST", "latitude": 40.7128, "longitude": -74.0060}]

        save_service_requests(data, str(data_file))

        with open(data_file) as f:
            saved = json.load(f)
        assert saved == data

    def test_formats_output_json_with_indentation(self, tmp_path):
        data_file = tmp_path / "data.json"
        data = [{"address": "123 MAIN ST"}]

        save_service_requests(data, str(data_file))

        content = data_file.read_text()
        assert "\n" in content


class TestMain:
    @patch("geocode.__main__.geocode_addresses")
    @patch("geocode.__main__.save_service_requests")
    @patch("geocode.__main__.load_service_requests")
    def test_calls_load_geocode_and_save_in_sequence(
        self, mock_load, mock_save, mock_geocode
    ):
        mock_load.return_value = [{"address": "123 MAIN ST"}]

        main()

        mock_load.assert_called_once()
        mock_geocode.assert_called_once()
        mock_save.assert_called_once()

    @patch("geocode.__main__.geocode_addresses")
    @patch("geocode.__main__.save_service_requests")
    @patch("geocode.__main__.load_service_requests")
    def test_passes_loaded_service_requests_to_geocode_addresses(
        self, mock_load, mock_save, mock_geocode
    ):
        data = [{"address": "123 MAIN ST"}]
        mock_load.return_value = data

        main()

        mock_geocode.assert_called_once_with(data)

    @patch("geocode.__main__.geocode_addresses")
    @patch("geocode.__main__.save_service_requests")
    @patch("geocode.__main__.load_service_requests")
    def test_saves_service_requests_after_geocoding(
        self, mock_load, mock_save, mock_geocode
    ):
        data = [{"address": "123 MAIN ST"}]
        mock_load.return_value = data

        main()

        mock_save.assert_called_once_with(data)
