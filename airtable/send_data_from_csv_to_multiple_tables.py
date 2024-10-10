from abstra.forms import Page, display
import os
import requests
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


# info markdown
md = """
### Expected Collumns

- First Name
- Last Name
- Email
- Person Linkedin Url
- Job Title
- Company
- Inudustry
- Number Of Employees
- Company Linkedin Url
- Website
"""

page = (
    Page()
    .display_markdown(md)
    .read_file("Upload the contact csv file", key="file_response")
    .run(validate=validate_file)
)

# Convert file to pandas dataframe
df = pd.read_csv(page["file_response"].file, on_bad_lines="skip")
print(df)


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
            "headcount": row["Number Of Employees"],
            "Linkedin": row["Company Linkedin Url"]
            if not pd.isnull(row["Company Linkedin Url"])
            else None,
            "website": row["Website"] if not pd.isnull(row["Website"]) else None,
        }
    }
    company_response = create_record("companies", company_data)
    company_id = company_response["id"] if company_response else None
    company_name = company_response["fields"]["name"] if company_response else None

    # 2 - Create Contact linked to the Company
    contact_data = {
        "fields": {
            "name": row["First Name"] + " " + row["Last Name"],
            "primary_email": row["Email"] if not pd.isnull(row["Email"]) else None,
            "linkedin_profile": row["Person Linkedin Url"]
            if not pd.isnull(row["Email"])
            else None,
            "job_title": row["Job Title"] if not pd.isnull(row["Email"]) else None,
            "company": [company_id],
        }
    }
    contact_response = create_record("contacts", contact_data)

display("Import complete! 🎉")
