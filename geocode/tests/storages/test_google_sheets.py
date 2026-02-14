from unittest.mock import patch, MagicMock
from geocode.storages.google_sheets import GoogleSheet


def mock_google_sheet():
    with patch("gspread.authorize") as mock_authorize, patch(
        "google.oauth2.service_account.Credentials.from_service_account_info"
    ) as mock_creds, patch("os.getenv") as mock_getenv:
        mock_getenv.return_value = '{"dummy": "creds"}'
        mock_creds.return_value = MagicMock()
        mock_client = MagicMock()
        mock_sheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_client.open_by_key.return_value = mock_sheet
        mock_sheet.worksheet.return_value = mock_worksheet
        mock_authorize.return_value = mock_client
        yield mock_worksheet


@patch("os.getenv", return_value='{"dummy": "creds"}')
@patch("google.oauth2.service_account.Credentials.from_service_account_info")
@patch("gspread.authorize")
def test_read_returns_records(mock_authorize, mock_creds, mock_getenv):
    mock_client = MagicMock()
    mock_sheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_records.return_value = [{"foo": "bar"}]
    mock_client.open_by_key.return_value = mock_sheet
    mock_sheet.worksheet.return_value = mock_worksheet
    mock_authorize.return_value = mock_client
    mock_creds.return_value = MagicMock()

    google_sheet = GoogleSheet("sheet_id", "worksheet", "ENV_VAR")
    result = google_sheet.read()

    assert result == [{"foo": "bar"}]


@patch("os.getenv", return_value='{"dummy": "creds"}')
@patch("google.oauth2.service_account.Credentials.from_service_account_info")
@patch("gspread.authorize")
def test_update_calls_clear_and_update(mock_authorize, mock_creds, mock_getenv):
    mock_client = MagicMock()
    mock_sheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_client.open_by_key.return_value = mock_sheet
    mock_sheet.worksheet.return_value = mock_worksheet
    mock_authorize.return_value = mock_client
    mock_creds.return_value = MagicMock()

    google_sheet = GoogleSheet("sheet_id", "worksheet", "ENV_VAR")
    service_requests = [{"a": 1, "b": 2}]
    google_sheet.update(service_requests)

    mock_worksheet.clear.assert_called_once()
    mock_worksheet.update.assert_called_once()


@patch("os.getenv", return_value='{"dummy": "creds"}')
@patch("google.oauth2.service_account.Credentials.from_service_account_info")
@patch("gspread.authorize")
def test_update_warns_on_empty(mock_authorize, mock_creds, mock_getenv):
    mock_client = MagicMock()
    mock_sheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_client.open_by_key.return_value = mock_sheet
    mock_sheet.worksheet.return_value = mock_worksheet
    mock_authorize.return_value = mock_client
    mock_creds.return_value = MagicMock()

    google_sheet = GoogleSheet("sheet_id", "worksheet", "ENV_VAR")
    # Should not call clear or update
    google_sheet.update([])

    mock_worksheet.clear.assert_not_called()
    mock_worksheet.update.assert_not_called()
