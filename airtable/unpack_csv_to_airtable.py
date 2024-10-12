from abstra.forms import Page, display
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import json

# Environment variables for API key and Base ID
load_dotenv()
airtable_token = os.environ.get("AIRTABLE_TOKEN")
airtable_base_id = os.environ.get("AIRTABLE_BASE_ID")


# Get csv file
def validate_file(page):
    if page.get("file_response") is not None:
        if not page["file_response"].file.name.endswith(".csv"):
            return "Uploaded file must be a CSV file"
    return True


page = (
    Page()
    .read_file("Upload the contact csv file", key="file_response")
    .run(validate=validate_file)
)

# Convert file to pandas dataframe
df = pd.read_csv(page["file_response"].file, on_bad_lines="skip")
print(df)

# Get required inputs from the user
deal_details = (
    Page()
    .display("Input deal details for deals created from this import", size="large")
    .display("🚨 All deals created will use the same details!", size="small")
    .read_dropdown(
        "Source",
        [
            "eventos",
            "ads - linkedin",
            "referral",
            "cold",
            "orgânico",
            "community - Grupo dos CTOs",
            "previous relationship",
            "ads - google",
            "ads - youtube",
            "previous lead",
            "existing customer",
            "investor intro",
        ],
    )
    .read_dropdown(
        "First touch",
        [
            "email",
            "whatsapp",
            "linkedin",
            "telefone",
            "evento",
            "intro presencial",
            "waiting list - Workflows",
            "form - schedule a demo",
            "discord",
            "slack",
            "form - abstra for startups",
        ],
    )
    .read_multiple_choice("Motion", ["inbound", "outbound", "expansion"])
    .read_dropdown(
        "Status",
        [
            "mapped",
            "closed_won",
            "closed_lost",
            "presenting",
            "prospected",
            "proposal_sent",
            "buy_in",
            "negotiation",
            "contract_signed",
            "first_meeting_scheduled",
        ],
    )
    .read("Cohort name")
    .run()
)

approve = (
    Page()
    .display("Records to be created", size="large", full_width=True)
    .display_pandas(df)
    .run(actions=["Cancel", "Continue"])
)

if approve.action == "Cancel":
    display("Import cancelled 🚫")
    exit()

# Set up the request to Airtable
headers = {
    "Authorization": f"Bearer {airtable_token}",
    "Content-Type": "application/json",
}
airtable_api_url = f"https://api.airtable.com/v0/{airtable_base_id}/"

response = requests.post(
    f"{airtable_api_url}cohorts",
    headers=headers,
    data=json.dumps(
        {
            "fields": {
                "name": deal_details["Cohort name"],
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
        }
    ),
)

print(response.json())
response = response.json() if response.status_code == 200 else None
cohort_id = response["id"] if response else None
print(cohort_id)


# Function to create a record in a table
def create_record(table, data):
    response = requests.post(
        f"{airtable_api_url}{table}", headers=headers, data=json.dumps(data)
    )
    if response.status_code == 200:
        print(
            f"Successfully created record in {table}. Response Code: {response.status_code}"
        )
        return response.json()
    else:
        print(
            f"Failed to create record in {table}. Response Code: {response.status_code}. Details: {response.text}"
        )
        return None


for index, row in df.iterrows():
    # 1 - Create company
    company_data = {
        "fields": {
            "name": row["Company"],
            "industry": row["Industry"],
            "headcount": row["# Employees"],
            "Linkedin": row["Company Linkedin Url"]
            if not pd.isnull(row["Company Linkedin Url"])
            else None,
            "website": row["Website"] if not pd.isnull(row["Website"]) else None,
        }
    }
    company_response = create_record("companies", company_data)
    company_id = company_response["id"] if company_response else None
    company_name = company_response["fields"]["name"] if company_response else None

    if not company_id:
        continue  # Skip this row if company creation failed

    # 2 - Create Contact linked to the Company
    contact_data = {
        "fields": {
            "name": row["First Name"] + " " + row["Last Name"],
            "primary_email": row["Email"] if not pd.isnull(row["Email"]) else None,
            "linkedin_profile": row["Person Linkedin Url"]
            if not pd.isnull(row["Email"])
            else None,
            "job_title": row["Title"] if not pd.isnull(row["Email"]) else None,
            "company": [company_id],
        }
    }
    contact_response = create_record("contacts", contact_data)
    contact_id = contact_response["id"] if contact_response else None
    contact_name = contact_response["fields"]["name"] if contact_response else None

    if not contact_id:
        continue  # Skip creating a deal if contact creation failed

    # 3 - Create Deal linked to the Company and Contact
    deal_data = {
        "fields": {
            "name": company_name + " - " + contact_name,
            "company": [company_id],
            "contacts": [contact_id],
            "source": deal_details["Source"],
            "first_touch": deal_details["First touch"],
            "motion": deal_details["Motion"],
            "status": deal_details["Status"],
            "cohort": [cohort_id],
        }
    }
    create_record("deals", deal_data)

display("Import complete! 🎉")
