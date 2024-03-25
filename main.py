import logging

from yaml import load, Loader

from notion_gsheet_api_sync.notion_handler import NotionDatabaseRead
from notion_gsheet_api_sync.gsheet_handler import GoogleWriter

log = logging.getLogger(__name__)


def main(config_dict):
    notion_api_key = config_dict["notion"]["api_key"]
    gsheet_credentials_file = config_dict["google"]["credentials_file"]

    notion_databases = {}
    for db in config_dict["notion"]["databases"]:
        label = list(db.keys())[0]
        notion_databases[label] = db[label]

    gsheet_spreadsheets = {}
    for sheet in config_dict["google"]["spreadsheets"]:
        label = list(sheet.keys())[0]
        gsheet_spreadsheets[label] = sheet[label]

    reader = NotionDatabaseRead(notion_api_key, notion_databases)
    writer = GoogleWriter(gsheet_credentials_file, gsheet_spreadsheets)

    for db_label in notion_databases:
        reader.query_db(db_label)

    for sheet_label in gsheet_spreadsheets:
        writer.write_data(sheet_label)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    with open('config.yaml', 'r') as yml:
        config = load(yml, Loader=Loader)
    main(config)
