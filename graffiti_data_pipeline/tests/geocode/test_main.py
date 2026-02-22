from unittest.mock import patch, Mock
from graffiti_data_pipeline.geocode.__main__ import main


@patch("graffiti_data_pipeline.geocode.__main__.get_logger")
@patch("graffiti_data_pipeline.geocode.__main__.JsonFile")
@patch("graffiti_data_pipeline.geocode.__main__.geocode_addresses")
def test_main_loads_geocodes_and_saves(mock_geocode, mock_jsonfile, mock_logger):
    logger_mock = Mock()
    mock_cache = Mock()
    mock_jsonfile.return_value = mock_cache
    mock_cache.load.return_value = [{"address": "123 MAIN ST"}]

    from graffiti_data_pipeline.geocode import __main__

    with patch.object(__main__, "logger", logger_mock):
        main()

    mock_cache.load.assert_called_once()
    mock_geocode.assert_called_once_with(mock_cache.load.return_value)
    mock_cache.save.assert_called_once_with(mock_cache.load.return_value)
    logger_mock.info.assert_any_call("Starting geocoding process")
    logger_mock.info.assert_any_call("Loaded 1 service requests")
    logger_mock.info.assert_any_call("Geocoding complete")


@patch("graffiti_data_pipeline.geocode.__main__.get_logger")
@patch("graffiti_data_pipeline.geocode.__main__.JsonFile")
@patch("graffiti_data_pipeline.geocode.__main__.geocode_addresses")
def test_main_handles_empty_service_requests(mock_geocode, mock_jsonfile, mock_logger):
    mock_logger.return_value = Mock()
    mock_cache = Mock()
    mock_jsonfile.return_value = mock_cache
    mock_cache.load.return_value = []

    main()

    mock_geocode.assert_called_once_with([])
    mock_cache.save.assert_called_once_with([])


@patch("graffiti_data_pipeline.geocode.__main__.get_logger")
@patch("graffiti_data_pipeline.geocode.__main__.JsonFile")
@patch("graffiti_data_pipeline.geocode.__main__.geocode_addresses")
def test_main_handles_malformed_service_requests(
    mock_geocode, mock_jsonfile, mock_logger
):
    mock_logger.return_value = Mock()
    mock_cache = Mock()
    mock_jsonfile.return_value = mock_cache
    malformed = [{"foo": "bar"}]
    mock_cache.load.return_value = malformed

    main()

    mock_geocode.assert_called_once_with(malformed)
    mock_cache.save.assert_called_once_with(malformed)


@patch("graffiti_data_pipeline.geocode.__main__.get_logger")
@patch("graffiti_data_pipeline.geocode.__main__.JsonFile")
@patch("graffiti_data_pipeline.geocode.__main__.geocode_addresses")
def test_main_geocode_addresses_raises_exception(
    mock_geocode, mock_jsonfile, mock_logger
):
    logger_mock = Mock()
    mock_cache = Mock()
    mock_jsonfile.return_value = mock_cache
    mock_cache.load.return_value = [{"address": "123 MAIN ST"}]
    mock_geocode.side_effect = Exception("geocode error")

    from graffiti_data_pipeline.geocode import __main__

    with patch.object(__main__, "logger", logger_mock):
        try:
            main()
        except Exception:
            pass

    logger_mock.info.assert_any_call("Starting geocoding process")
    logger_mock.info.assert_any_call("Loaded 1 service requests")


@patch("graffiti_data_pipeline.geocode.__main__.get_logger")
@patch("graffiti_data_pipeline.geocode.__main__.JsonFile")
@patch("graffiti_data_pipeline.geocode.__main__.geocode_addresses")
def test_main_save_fails(mock_geocode, mock_jsonfile, mock_logger):
    logger_mock = Mock()
    mock_cache = Mock()
    mock_jsonfile.return_value = mock_cache
    mock_cache.load.return_value = [{"address": "123 MAIN ST"}]
    mock_cache.save.side_effect = Exception("save error")

    from graffiti_data_pipeline.geocode import __main__

    with patch.object(__main__, "logger", logger_mock):
        main()

    logger_mock.info.assert_any_call("Starting geocoding process")
    logger_mock.info.assert_any_call("Loaded 1 service requests")
