import os
import json

import gspread
from google.oauth2.service_account import Credentials

from geocode.logger import get_logger

logger = get_logger(__name__)


class GoogleSheet:
    def __init__(self, sheet_identifier, worksheet_name, creds_env_var):
        self._creds_env_var = creds_env_var
        credentials_json = os.getenv(creds_env_var)

        if not credentials_json:
            raise RuntimeError(
                f"Missing Google service account JSON in env var: {creds_env_var}"
            )

        credentials = Credentials.from_service_account_info(
            json.loads(credentials_json),
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        self._google_client = gspread.authorize(credentials)
        self._google_sheet = self._google_client.open_by_key(sheet_identifier)
        self.worksheet = self._google_sheet.worksheet(worksheet_name)

    def read(self):
        """Reads all graffiti service requests from the worksheet as a list of dicts."""
        return self.worksheet.get_all_records()

    def update(self, service_requests: list[dict]):
        """Updates the worksheet with graffiti service requests from a JSON file."""
        if not service_requests:
            logger.warning("No service requests to update.")
            return

        headers = list(service_requests[0].keys())
        rows = [headers] + [list(req.values()) for req in service_requests]
        self.worksheet.clear()
        self.worksheet.update(rows)
        logger.info(f"Updated worksheet with {len(service_requests)} service requests.")
