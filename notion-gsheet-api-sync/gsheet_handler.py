import json
import logging
import sys

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from yaml import load, Loader

log = logging.getLogger(__name__)


class GoogleWriter:
    def __init__(self, credentials_file: str, spreadsheets: dict) -> None:
        self.spreadsheets = spreadsheets
        log.debug(f"Using the following spreadsheets configuration:\n {spreadsheets}")

        self.SCOPES = [
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets",
        ]

        self.creds = self.get_credentials_from_tokenjson(credentials_file)

        self.sheets = self.authenticate_sheets(self.creds)

    def get_credentials_from_tokenjson(self, filepath):
        return Credentials.from_authorized_user_file(filepath, self.SCOPES)

    def authenticate_sheets(self, creds):
        log.debug("Attempting to authenticate google sheets api")
        return build("sheets", "v4", credentials=creds).spreadsheets()

    def load_json_data(self, json_filepath: str):
        pass

    def write_data(self, sheet_label: str):
        with open(self.sheets[sheet_label]['input_json'], 'r') as data:
            pass

    def build_row(self, json_dict: dict):
        pass

    def get_sheet_header(self, json_dict: dict):
        pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    with open("config.yaml", "r") as yml:
        config = load(yml, Loader=Loader)

    credentials_file = config["google"]["credentials_file"]
    spreadsheets = {}
    for sheet in config["google"]["spreadsheets"]:
        label = list(sheet.keys())[0]
        spreadsheets[label] = sheet[label]

    writer = GoogleWriter(credentials_file, spreadsheets)
