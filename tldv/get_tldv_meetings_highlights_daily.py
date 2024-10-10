import datetime
import json
import os
import requests
from abstra.common import get_persistent_dir


API_KEY = os.getenv("TLDV_API_KEY")
CONTENT_TYPE = "application/json"

persistent_dir = get_persistent_dir()
folder_path = persistent_dir / "tldv-meetings"
file_path = (
    f"{folder_path}/meetings-{datetime.datetime.now().strftime('%Y-%m-%d')}.json"
)


def separate_highlights_by_label(highlights: list[dict]) -> dict:
    separated = {}

    for h in highlights:
        label = h["category"].get("label", None)

        if label not in separated:
            separated[label] = ""
        separated[label] += f"{h['text']}\n"

    return separated


def get_todays_meetings() -> list[dict]:
    url = "https://pasta.tldv.io/v1alpha1/meetings"

    headers = {
        "Content-Type": CONTENT_TYPE,
        "x-api-key": API_KEY,
    }
    params = {
        "from": (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        ),
        "to": (datetime.datetime.now()).strftime("%Y-%m-%d"),
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("error getting meetings: ", err)
        raise err

    response_json = response.json()

    return response_json.get("results", [])


def get_meetings_highlights(meeting_id: str) -> list:
    url = f"https://pasta.tldv.io/v1alpha1/meetings/{meeting_id}/highlights"

    headers = {
        "Content-Type": CONTENT_TYPE,
        "x-api-key": API_KEY,
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("error getting highlights: ", err)
        raise err

    response_json = response.json()

    return response_json.get("data", [])


meetings = get_todays_meetings()

for meeting in meetings:
    meeting_id = meeting["id"]
    highlights = get_meetings_highlights(meeting_id)
    meeting["highlights"] = separate_highlights_by_label(highlights)


if not os.path.exists(folder_path):
    os.makedirs(folder_path)

with open(file_path, "w") as f:
    json.dump(meetings, f, indent=4)
