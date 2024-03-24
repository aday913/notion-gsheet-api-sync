import json
import logging
import string
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
        with open(self.spreadsheets[sheet_label]["input_json"], "r") as data:
            notion_results = json.load(data)
            first_item = notion_results["results"][0]
            header = self.get_sheet_header(first_item)
            spreadsheetId = self.spreadsheets[sheet_label]["id"]
            self.write_gsheet_header(header=header, spreadsheetId=spreadsheetId)

    def build_row(self, json_dict: dict):
        pass

    def get_sheet_header(self, json_dict: dict):
        header = []
        for property in json_dict["properties"]:
            header.append(property)
        log.debug(f"Got the following header from the input json:\n {header}")
        return header

    def write_gsheet_header(self, header: list, spreadsheetId: str):
        last_letter = self.list_length_to_column(len(header))
        body = {
            "majorDimension": "ROWS",
            "range": f"A1:{last_letter}1",
            "values": [header],
        }
        self.sheets.values().update(
            spreadsheetId=spreadsheetId,
            range=f"A1:{last_letter}1",
            body=body,
            valueInputOption="RAW",
        ).execute()

    def list_length_to_column(self, length):
        """
        Converts a list length to a corresponding column letter (like in Google Sheets).

        Args:
            length: The length of the list (integer).

        Returns:
            A string representing the column letter.
        """

        letters = string.ascii_uppercase
        result = ""
        while length > 0:
            # Because indexing starts at 0, we subtract 1
            index = (length - 1) % 26
            result = letters[index] + result
            length = (length - 1) // 26  # Integer division for prefix calculation
        return result


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

    writer.write_data("book_shelf")
