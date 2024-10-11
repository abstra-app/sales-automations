from datetime import timedelta, datetime
from dateutil.tz import gettz
from abstra.tables import select_one, insert

import pytz
from abstra.forms import url_params, Page, ListItemSchema, execute_js, display_markdown
from abstra.workflows import set_data

from calendar_utils import DatetimeRange, get_date_options, schedule_event

url = url_params.get("url")
print(f"Referring URL: {url}")

GOAL_TIMEZONE = pytz.timezone("America/Sao_Paulo")
BROWSER_TIMEZONE = pytz.timezone(
    str(execute_js("Intl.DateTimeFormat().resolvedOptions().timeZone"))
)
MIN_AVAILABLE_HOUR = 9
MAX_AVAILABLE_HOUR = 19
MEETING_SPACING = timedelta(minutes=15)
HOST_EMAILS = ["example@domain.com", "example@domain.com"]


info = (
    Page()
    .read("What's your name?", key="name", initial_value=url_params.get("name"))
    .read_email(
        "What's your email?", key="email", initial_value=url_params.get("email")
    )
    .read(
        "What's your company's name?",
        key="company",
        initial_value=url_params.get("company"),
    )
    .read_phone(
        "What's your phone number?",
        key="phone",
        required=False,
        initial_value=url_params.get("phone"),
    )
    .read_textarea(
        "What brings you here?", key="context", initial_value=url_params.get("context")
    )
    .read_multiple_choice(
        "How long would you like our call to be?",
        [{"label": "30 minutes", "value": 30}, {"label": "1 hour", "value": 60}],
        key="duration",
        initial_value=30,
    )
    .run("Next")
)

name = info["name"]
email = info["email"]
company = info["company"]
context = info["context"]
duration = info["duration"]
MEETING_TIME = timedelta(minutes=duration)

print(f"Name: {name}")
print(f"Email: {email}")
print(f"Company: {company}")
print(f"Context: {context}")
print(f"Duration: {duration}")

date_options = get_date_options(
    HOST_EMAILS,
    MEETING_TIME,
    MEETING_SPACING,
    GOAL_TIMEZONE,
    BROWSER_TIMEZONE,
    MIN_AVAILABLE_HOUR,
    MAX_AVAILABLE_HOUR,
)

item = ListItemSchema().read_email("Email")

add_emails = (
    Page()
    .display("If you'd like to add other people to the chat, add their emails below.")
    .read_list(item, key="email", required=False)
    .run("Schedule")
)

additional_emails = add_emails["email"] or []


# Schedule Event on google calendar
atendee = {"name": name, "email": email, "company": company}
event_range = DatetimeRange.decode(date_options["selected_slot"])
response: dict = schedule_event(
    HOST_EMAILS,
    event_range,
    atendee,
    additionalEmails=additional_emails,
    timezone=GOAL_TIMEZONE,
    context=f"Context: {context}. Referring URL: {url}",
)

print(f"""Meeting date: {date_options["selected_slot"]["start"]}""")
demo_date = date_options["selected_slot"]["start"]

demo_info = {
    "name": name,
    "email": email,
    "company": company,
    "context": context,
    "title": response.get("summary", f"Abstra <> {name} - {company}"),
    "demo_date": demo_date,
    "duration": duration,
    "referring_url": url,
    "origin": "Meet Bruno",
}

# register meeting to tables
google_id = response["id"]
print(response)
if select_one("google_calendar_events", where={"google_id": google_id}) is None:

    # start and end in UTC timezone
    start = datetime.strptime(response["start"]["dateTime"], "%Y-%m-%dT%H:%M:%S%z")
    end = datetime.strptime(response["end"]["dateTime"], "%Y-%m-%dT%H:%M:%S%z")

    insert("google_calendar_events", {
        "google_id": google_id,
        "title": demo_info["title"],
        "start": start.astimezone(gettz("UTC")),
        "end": end.astimezone(gettz("UTC")),
        "organizer_email": HOST_EMAILS[0],
        "company_name": demo_info["company"],
    })

phone = info.get("phone", None)
if phone:
    demo_info["phone"] = phone
    
set_data("deal_applicable", 'false')
set_data("demo_info", demo_info)
set_data("form_type", "Meet Bruno")


display_markdown(
    f"""
## Your chat is scheduled for {event_range.start.strftime('%m/%d/%Y %H:%M')}!

Check your email for a calendar invite.

See you there 👋🏼
""",
    end_program=True,
)
