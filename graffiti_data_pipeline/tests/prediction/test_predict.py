import pytest
from unittest.mock import patch, MagicMock
from graffiti_data_pipeline.prediction import predict


class TestPredictMain:
    @patch("graffiti_data_pipeline.prediction.predict.JsonFile")
    @patch("graffiti_data_pipeline.prediction.predict.get_logger")
    def test_main_runs_and_enriches(self, mock_logger, mock_jsonfile):
        mock_logger.return_value = MagicMock()
        mock_cache = MagicMock()
        mock_jsonfile.return_value = mock_cache
        mock_cache.load.return_value = [
            {
                "address": "123 MAIN ST, Manhattan",
                "last_updated": "2026-02-01",
                "created": "2026-01-01",
                "status": "Site to be cleaned.",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "unique_key": "123-main-st",
            }
        ]
        mock_cache.save.return_value = None
        predict.main()
        mock_cache.load.assert_called_once()
        mock_cache.save.assert_called_once()

    @patch("graffiti_data_pipeline.prediction.predict.JsonFile")
    @patch("graffiti_data_pipeline.prediction.predict.get_logger")
    def test_main_handles_empty_records(self, mock_logger, mock_jsonfile):
        mock_logger.return_value = MagicMock()
        mock_cache = MagicMock()
        mock_jsonfile.return_value = mock_cache
        mock_cache.load.return_value = []
        mock_cache.save.return_value = None
        with pytest.raises(ValueError):
            predict.main()
        mock_cache.load.assert_called_once()

    @patch("graffiti_data_pipeline.prediction.predict.JsonFile")
    @patch("graffiti_data_pipeline.prediction.predict.get_logger")
    def test_main_handles_invalid_record(self, mock_logger, mock_jsonfile):
        mock_logger.return_value = MagicMock()
        mock_cache = MagicMock()
        mock_jsonfile.return_value = mock_cache
        mock_cache.load.return_value = [123]
        mock_cache.save.return_value = None
        with pytest.raises(Exception):
            predict.main()

    @patch("graffiti_data_pipeline.prediction.predict.JsonFile")
    @patch("graffiti_data_pipeline.prediction.predict.get_logger")
    def test_main_save_failure(self, mock_logger, mock_jsonfile):
        mock_logger.return_value = MagicMock()
        mock_cache = MagicMock()
        mock_jsonfile.return_value = mock_cache
        mock_cache.load.return_value = [
            {
                "address": "123 MAIN ST, Manhattan",
                "last_updated": "2026-02-01",
                "created": "2026-01-01",
                "status": "Site to be cleaned.",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "unique_key": "123-main-st",
            }
        ]
        mock_cache.save.side_effect = Exception("Save failed")
        with pytest.raises(Exception):
            predict.main()

    @patch("graffiti_data_pipeline.prediction.predict.JsonFile")
    @patch("graffiti_data_pipeline.prediction.predict.get_logger")
    def test_main_handles_incomplete_record(self, mock_logger, mock_jsonfile):
        mock_logger.return_value = MagicMock()
        mock_cache = MagicMock()
        mock_jsonfile.return_value = mock_cache
        mock_cache.load.return_value = [{"address": "no fields"}]
        mock_cache.save.return_value = None
        predict.main()
        mock_cache.save.assert_called_once()
