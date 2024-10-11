from datetime import datetime, timedelta
from pipedrive import Activity, Deal, Person, Organization


def name_from_email(email: str):
    return " ".join([e.capitalize() for e in email.split("@")[0].split(".")])


owner_id = 1  # ID of the user to assign the deal
emails = ["john.doe@domain.com", "mary.lee@domain.com"]  # list of emials to add to CRM
organization_name = "Domain Inc"  # name of the organization to add to CRM

pipedrive_contacts: list[Person] = []
pipedrive_contacts_ids: list[int] = []
company_domain = None


# Organization
# Add / retrieve organization
existent_orgs = Organization.retrieve_by(name=organization_name)

if len(existent_orgs) == 0:
    organization = Organization.create(name=organization_name, owner_id=owner_id)
    print(f"Organization created: {organization.name}")

else:
    organization = existent_orgs[0]
    print(f"Organization already exists: {organization.name}")


# People
# Add / retrieve people
for email in emails:
    existent_people = Person.retrieve_by(email=email)

    if len(existent_people) == 0:
        person = Person.create(
            name=name_from_email(email), 
            email=email, 
            org_id=organization.id, 
            owner_id=owner_id
        )
        print(f"Person created: {person.name}")

    else:
        person = existent_people[0]
        print(f"Person already exists: {person.name}")

    pipedrive_contacts.append(person)
    pipedrive_contacts_ids.append(person.id)


# Deals
# try to retrieve by company domain
existent_deals = Deal.get_all_deals()
deal = None

for d in existent_deals:
    if d.person_id in pipedrive_contacts_ids and d.org_id == organization.id:
        deal = d
        print(f"Deal found: {deal.title}")
        break

# if no deal found, create a new one
if deal is None:
    deal = Deal.create(
        title=f"New Trial - {pipedrive_contacts[0].name}",
        person_id=pipedrive_contacts[0].id,
        stage_id=1,
        pipeline_id=1,
        owner_id=owner_id,
    )

# Add participants to deal
for p in pipedrive_contacts_ids:
    deal.add_participant(p)


# Activities
# Add activity trial start
now = datetime.now()
follow_up = now + timedelta(days=7)
date_str = follow_up.strftime("%Y-%m-%d")
time_str = follow_up.strftime("%H:%M:%S")

activity = Activity.create(
    deal_id=deal.id,
    subject="Follow up",
    due_date=date_str,
    due_time=time_str,
    type=Activity.Type.follow_up,
    participants_ids=pipedrive_contacts_ids,
    done=False,
)

