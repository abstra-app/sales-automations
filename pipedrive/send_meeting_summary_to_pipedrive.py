import datetime
from abstra_internals.constants import STAGE_RUN_ID_PARAM_KEY
from dateutil.tz import gettz
import json

from abstra.common import get_persistent_dir
from pipedrive import Activity, Person, Deal


# Id of pipedrive user that will own the deals
OWNER_ID = 1
PILELINE_ID = 1
STAGE_ID = 1


persistent_dir = get_persistent_dir()
file_path = (
    persistent_dir
    / f"tldv-meetings/meetings-{datetime.datetime.now().strftime('%Y-%m-%d')}.json"
)


def has_common_elements(list1, list2):
    if (list1 is None) or (list2 is None):
        return False
    return not set(list1).isdisjoint(set(list2))


def name_from_email(email: str):
    return " ".join([e.capitalize() for e in email.split("@")[0].split(".")])


# format highlights dct in a single string
def format_highlights(highlights):
    formatted = ""
    for h in highlights:
        formatted += f"{h}:\n"
        formatted += f"{highlights[h]}\n"

    return formatted


tldv_meetings = []


# data from todays meetings
try:
    with open(file_path, "r") as f:
        tldv_meetings = json.load(f)
except FileNotFoundError:
    print("Meetings file not found")
    raise SystemExit


# run through meetings, check if invitee exists, add info to log_records
for meeting in tldv_meetings:
    highlight = format_highlights(meeting["highlights"])
    organizer_email = meeting["organizer"]["email"]
    meeting_title = meeting["name"]

    meeting_timestamp = meeting["happenedAt"]
    meeting_datetime_obj = datetime.datetime.strptime(
        meeting_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    meeting_datetime_obj = meeting_datetime_obj.replace(
        tzinfo=gettz("America/Sao_Paulo")
    )
    meeting_datetime_obj = meeting_datetime_obj.astimezone(gettz("UTC"))
    meeting_timestamp = meeting_datetime_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    meeting_dict = {"title": meeting_title, "timestamp": meeting_timestamp}

    invitees = meeting["invitees"] + [meeting["organizer"]]

    # first, locate which invitees are already in pipedrive
    pipedrive_contacts: list[Person] = []
    people_to_add = []
    organization_id = None

    for inv in invitees:
        existent_people = Person.retrieve_by(email=inv["email"])

        if existent_people:
            pipedrive_contacts.append(existent_people[0])
            organization_id = (
                existent_people[0].organization_id
                if not organization_id
                else organization_id
            )
        else:
            people_to_add.append(inv)

    print(f"pipedrive contacts: {[p.name for p in pipedrive_contacts]}")
    print(f"people to add: {people_to_add}")

    # deal with new contacts
    for inv in people_to_add:
        new_person = Person.create(
            name=inv["name"],
            email=inv["email"],
            org_id=organization_id,
            owner_id=OWNER_ID,
            phone=None,
            job_title=None,
            linkedin=None,
        )

        pipedrive_contacts.append(new_person)
        print(f"added {new_person.name} to pipedrive")

    pipedrive_contacts_ids = [p.id for p in pipedrive_contacts]

    # Create Deal
    created_deal = Deal.create(
        title=meeting_title,
        person_id=pipedrive_contacts[0].id,
        org_id=organization_id,
        owner_id=OWNER_ID,
        pipeline_id=PILELINE_ID,
        stage_id=STAGE_ID,
        company_domain=pipedrive_contacts[0].extract_domain(),
    )
    deal_id = created_deal.id
    print(f"deal created: {created_deal.title}")

    # Create Activity
    Activity.create(
        subject=meeting_title,
        deal_id=deal_id,
        type="Meeting",
        note=meeting["url"] + " // " + highlight,
        due_date=meeting_timestamp.split("T")[0],
        due_time=meeting_timestamp.split("T")[1][0:5],
        duration="00:30",
        participants_ids=pipedrive_contacts_ids,
        done=True,
    )
    print(f"activity created: {meeting_title}")
