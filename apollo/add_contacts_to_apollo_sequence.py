import json
import os
import requests
import pandas as pd
from abstra.common import get_persistent_dir
from abstra.workflows import get_data


API_KEY = os.getenv("APOLLO_API_KEY")
CONTENT_TYPE = "application/json"

form_info = get_data("form_info")


def verify_if_contact_exists(contact):
    url = "https://api.apollo.io/v1/contacts/search"

    data = {
        "api_key": API_KEY,
        "q_keywords": f"{contact['first_name']} {contact['last_name']}, {contact['organization_name']}, {contact['email']}",
        "sort_ascending": False,
    }

    headers = {"Cache-Control": "no-cache", "Content-Type": CONTENT_TYPE}

    response = requests.request("POST", url, headers=headers, json=data)
    response_json = json.loads(response.text)

    if len(response_json.get("contacts", [])) > 0:
        return response_json["contacts"][0]["id"]
    else:
        return None


def add_contact(contact):
    url = "https://api.apollo.io/v1/contacts"

    data = {
        "api_key": API_KEY,
        "first_name": contact["first_name"],
        "last_name": contact["last_name"],
        "email": contact["email"],
        "organization_name": contact["organization_name"],
    }

    headers = {"Cache-Control": "no-cache", "Content-Type": CONTENT_TYPE}

    response = requests.request("POST", url, headers=headers, json=data)
    try:
        response_json = json.loads(response.text)
    except Exception as e:
        print("Error adding contact", e)
        print(response.text)
        raise Exception("Error adding contact")

    return response_json["contact"]["id"]


def add_to_sequence(contact_ids_array, sequence_id, mailer_id):
    url = f"https://api.apollo.io/v1/emailer_campaigns/{sequence_id}/add_contact_ids"

    data = {
        "api_key": API_KEY,
        "async": False,
        "contact_ids": contact_ids_array,
        "emailer_campaign_id": sequence_id,
        "send_email_from_email_account_id": mailer_id,
        "sequence_active_in_other_campaigns": False,
        "sequence_no_email": False,
        "sequence_finished_in_other_campaigns": False,
        "sequence_unverified_email": False,
        "sequence_job_change": False,
        "sequence_same_company_in_same_campaign": False,
    }

    headers = {"Cache-Control": "no-cache", "Content-Type": CONTENT_TYPE}

    requests.request("POST", url, headers=headers, json=data)


# Gorup contacts by sequence_id and mailer_id
# This is made so a group of cantacts can be added in a single request
def separate_contacts(contacts):
    separated_contacts = {}

    for contact in contacts:
        key = (form_info["sequence_id"], form_info["mailer_id"])
        if key not in separated_contacts:
            separated_contacts[key] = []
        separated_contacts[key].append(contact)

    return separated_contacts


persistent_dir = get_persistent_dir()
contacts = pd.read_csv(persistent_dir / "contacts.csv")
all_contacts = contacts.to_dict(orient="records")

if len(all_contacts):
    contacts = separate_contacts(all_contacts)

    contact_ids = []

    for key, value in contacts.items():
        for contact in value:
            contact_id = verify_if_contact_exists(contact)

            if contact_id is None:
                contact_id = add_contact(contact)

            contact_ids.append(contact_id)

        add_to_sequence(contact_ids, key[0], key[1])
