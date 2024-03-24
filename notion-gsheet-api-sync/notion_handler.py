import json
import logging
import sys

import requests
from yaml import load, Loader

log = logging.getLogger(__name__)


class NotionDatabaseRead:
    def __init__(self, api_key: str, databases: dict):
        self.API_KEY = api_key
        self.databases = databases
        log.debug(f"Using the following database configuration:\n {self.databases}")

        self.url = "https://api.notion.com/v1/databases"
        self.headers = {
            "Authorization": f"{self.API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    def query_db(self, db_label: str, filter_json: dict = {}):
        try:
            db = self.databases[db_label]
        except KeyError:
            log.error(f"No database with label {db_label} found")
            return

        log.debug("Fetching database id")
        db_id = db["id"]
        log.debug(f"Found database ID {db_id}")

        has_more = True
        next_cursor = 'undefined'
        results_json = {"results": []}
        body_json = {}
        if filter_json != {}:
            body_json["filter"] = filter_json
        num_queries = 1
        try:
            while has_more:
                response = requests.api.post(
                    f"{self.url}/{db_id}/query", headers=self.headers, json=body_json
                )
                formatted_response = response.json()
                for result in formatted_response["results"]:
                    results_json["results"].append(result)
                has_more = bool(formatted_response["has_more"])
                next_cursor = formatted_response["next_cursor"]
                body_json["start_cursor"] = next_cursor
                log.debug(
                    f'At the end of query {num_queries}, has_more is {has_more}, next_cursor is {next_cursor}, and there are {len(results_json["results"])} results'
                )
                num_queries += 1
        except Exception as error:
            log.error(f"Got the following error when querying db: {error}")
            log.error(f"Here is the response: {response.json()}")
            sys.exit(1)

        log.info(f'Got {len(results_json["results"])} results from the query')
        log.info(f'Saving response json to output file {db["output"]}')
        with open(db["output"], "w") as f:
            json.dump(results_json, f, indent=2)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    with open("config.yaml", "r") as yml:
        config = load(yml, Loader=Loader)

    api_key = config["notion"]["api_key"]
    databases = {}
    for db in config["notion"]["databases"]:
        label = list(db.keys())[0]
        databases[label] = db[label]

    notionBot = NotionDatabaseRead(api_key, databases)

    notionBot.query_db("book_shelf")
