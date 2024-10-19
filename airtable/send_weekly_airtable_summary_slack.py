from abstra.common import get_persistent_dir
import datetime
import json
import os
import re
from slack_util import send_message


CHANNEL_ID = os.getenv("SLACK_CHANNEL")
if CHANNEL_ID is None:
    raise Exception("CHANNEL_ID env var not set.")

persistent_dir = get_persistent_dir()

folder_path = persistent_dir / "weekly-diff"
files_path = folder_path / f'{datetime.datetime.now().strftime("%Y-%m-%d")}.json'

diff = None
unchanged_entites = None

# identify the url pattern for one individual entity (entity id between curly brackets), for example:
url_pattern = "https://airtable.com/appKHwrhfjdkcbfdK/tbliedjsjtfsjdjOe/viwIrcseivfrfsseO/{entity_id}?blocks=hide"
slack_message_active = "Weekly Airtable Entities Diff"


# load data from respective files
with open(files_path, "r") as f:
    diff = json.load(f)

slack_message_active += f"From *{diff['from']}* to *{diff['to']}*:\n\n"


# create slack messages going through the diff
if len(diff.keys()) == 0:
    slack_message_active += "- No data available, file missing for this day."

elif len(diff.keys()) == 4 and len(diff["new_entites"]) == 0:
    slack_message_active += "- No changes in entites status."

else:
    for key in diff.keys():
        if key == "from" or key == "to" or key == "unchanged_entites":
            continue

        formatted = " ".join([w.capitalize() for w in re.split("_| ", key)])
        formatted = formatted.replace("->", "➜")

        slack_message_active += f"*{formatted}*:\n"

        for entites_id in diff[key]:
            hyperlink = url_pattern.format(entites_id=entites_id)
            slack_message_active += f"• <{hyperlink}|{diff[key][entites_id]}>\n"
        slack_message_active += "\n"


# send slack message for entiteschanges
send_message(slack_message_active, CHANNEL_ID)
