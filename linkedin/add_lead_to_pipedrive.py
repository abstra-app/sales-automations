import abstra.workflows as aw
from linkedin_api import get_creative
from pipedrive import Organization, Person, Deal


STAGE_ID = 1
PIPELINE_ID = 1
OWNER_ID = 1

# lead info
form_answer = aw.get_data("form_answer")
data = aw.get_data("lead")
ads_id = aw.get_data("campaign_id")
campaign_id = (get_creative(ads_id).get("campaign", "")).split(":")[-1]

contact = {
    "first_name": form_answer.get("FIRST_NAME", None),
    "last_name": form_answer.get("LAST_NAME", None),
    "email": form_answer.get("EMAIL", None),
    "organization_name": form_answer.get("COMPANY_NAME", None),
    "job_title": form_answer.get("JOB_TITLE", None),
    "phone": form_answer.get("PHONE_NUMBER", None),
    "linkedin_url": form_answer.get("LINKEDIN_PROFILE_LINK", None),
}


# create or retrieve org
existent_orgs = Organization.retrieve_by(name=contact["organization_name"])

if len(existent_orgs) == 0:
    organization = Organization.create(
        name=contact["organization_name"], owner_id=Deal.Owner.jessica
    )
else:
    organization = existent_orgs[0]

organization_id = organization.id


# create or retrieve person
existent_people = Person.retrieve_by(email=contact["email"])

if len(existent_people) == 0:
    person = Person.create(
        name=f"{contact['first_name']} {contact['last_name']}",
        email=contact["email"],
        org_id=organization_id,
        owner_id=OWNER_ID,
        phone=contact["phone"],
    )
else:
    person = existent_people[0]

person_id = person.id

# create deal
Deal.create(
    title=f"{contact['first_name']} {contact['last_name']} | {contact['organization_name']}",
    org_id=organization_id,
    person_id=person_id,
    stage_id=STAGE_ID,
    pipeline_id=PIPELINE_ID,
    owner_id=OWNER_ID,
)
