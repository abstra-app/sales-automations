import os
from io import BytesIO

import abstra.forms as af
import abstra.workflows as aw
import pandas as pd
import requests
from abstra.common import get_persistent_dir

API_KEY = os.getenv("APOLLO_API_KEY")
persistent_dir = get_persistent_dir()

# Register acconts that can send emails on Apollo
mailer_options = [
    {"label": "exampl@domain.com", "value": "mailer_id"},
]


def get_all_sequences():
    try:
        url = "https://api.apollo.io/v1/emailer_campaigns/search"

        data = {
            "api_key": API_KEY,
        }

        headers = {"Cache-Control": "no-cache", "Content-Type": "application/json"}

        response = requests.request("POST", url, headers=headers, json=data)
        response.raise_for_status()
        data = response.json()

        all_sequences = []

        for sequence in data["emailer_campaigns"]:
            all_sequences.append({"label": sequence["name"], "value": sequence["id"]})

        return all_sequences

    except Exception as e:
        print("Error getting sequences", e)
        af.display("No sequences found, try checking the API key.", end_program=True)
        raise Exception("No sequences found")


all_sequences = get_all_sequences()

id_info = (
    af.Page()
    .read_multiple_choice(
        "Select mailer of this sequence",
        mailer_options,
        initial_value="634f00525bf03100a3535fc2",
        key="mailer_id",
    )
    .read_dropdown(
        "Select sequence to add contacts",
        all_sequences,
        min=1,
        key="sequence_id",
    )
    .run()
)


# Recieve the sequence ID and mailer ID
sequence_id = id_info["sequence_id"]
sequence_name = [
    sequence["label"] for sequence in all_sequences if sequence["value"] == sequence_id
][0]
mailer_id = id_info["mailer_id"]

# Recieve the CSV file
contacts_page = (
    af.Page()
    .display_markdown(""""
### Expected Columns:

- id
- first_name
- last_name
- email
- organization_name
""")
    .read_file("Select the CSV file with the leads to add to the sequence:", key="file")
    .run()
)

file_respose = contacts_page["file"]
buffer = BytesIO(file_respose.content)
contacts_table = pd.read_csv(buffer)

selected_contacts = af.read_pandas_row_selection(
    contacts_table,
    label=f"Select leads to REMOVE from the sequence: {sequence_name}",
    multiple=True,
    full_width=True,
    required=False,
)

# select to remove
selected_indices = [contact["index"] for contact in selected_contacts]
contacts_table = contacts_table.drop(selected_indices)
contacts_table.to_csv(persistent_dir / "contacts.csv", index=False)

# select to add:
# df = pd.DataFrame(selected_contacts)
# df.to_csv(persistent_dir / "contacts.csv", index=False)
# contacts_list = df.to_dict("records")
# print(contacts_list)


form_info = {
    "sequence_id": sequence_id,
    "sequence_name": sequence_name,
    "mailer_id": mailer_id,
}

aw.set_data("form_info", form_info)
