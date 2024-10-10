# Track fields of a Airtable entity daily and report changes
# by the end of the week.

import requests
import os
import json
import datetime
from abstra.common import get_persistent_dir


CONTENT_TYPE = "application/json"
API_TOKEN = os.getenv("AIRTABLE_TOKEN")
TABLE_URL = "url of the entity table"
TABLE_URL = "https://api.airtable.com/v0/appKHwTmUuNQbROsK/deals"

# Replace acording to needs
IDENTIFIER_FIELD = "name"  # Field to be used as identifier (name, title, etc)
TRECKED_FIELD = "status"  # Field to be tracked

persistent_dir = get_persistent_dir()
folder_path = persistent_dir / "daily_entity_tracking"
save_path = folder_path / f"entity-tracking-{datetime.date.today()}.json"
formatted_entities = {}


# get the complete list of entities from Airtable
def list_all_entities() -> list:
    url = f"{TABLE_URL}?view=Grid%20view"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
    }

    # get API response and convert response to json
    response = requests.get(url, headers=headers)
    response_json = response.json()

    records = response_json.get("records", [])

    # entity with pagination if there are more than 100 records
    while "offset" in response_json:
        pagination_url = f"{url}&offset={response_json['offset']}"

        response = requests.get(pagination_url, headers=headers)
        response_json = response.json()

        records.extend(response_json.get("records", []))

    return records


# get the complete list of entities and return a dict with the id as key
def separate_by_id(entities: list) -> dict:
    status_dict = {}
    status_dict["date"] = datetime.date.today().strftime("%Y-%m-%d")

    for entity in entities:
        entity_id = entity["id"]
        if entity_id is not None:
            status_dict[entity_id] = {}

            status_dict[entity_id]["identifier"] = entity["fields"].get(
                IDENTIFIER_FIELD, None
            )
            status_dict[entity_id]["tracked"] = entity["fields"].get(
                TRECKED_FIELD, None
            )

    return status_dict


formatted_entities = separate_by_id(list_all_entities())

# save to json file
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

with open(save_path, "w") as f:
    json.dump(formatted_entities, f, indent=4)
