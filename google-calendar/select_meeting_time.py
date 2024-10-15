from datetime import timedelta
import pytz
from abstra.forms import Page, ListItemSchema, execute_js, display_markdown
from abstra.workflows import set_data

from calendar_utils import get_date_options

GOAL_TIMEZONE = pytz.timezone("America/Sao_Paulo")
BROWSER_TIMEZONE = pytz.timezone(
    str(execute_js("Intl.DateTimeFormat().resolvedOptions().timeZone"))
)
MIN_AVAILABLE_HOUR = 9
MAX_AVAILABLE_HOUR = 19
MEETING_SPACING = timedelta(minutes=15)
HOST_EMAILS = ["paim@abstra.app"]


# Basic user infromation
info = (
    Page()
    .read("What's your name?", key="name")
    .read_email("What's your email?", key="email")
    .read(
        "What's your company's name?",
        key="company",
    )
    .read_phone(
        "What's your phone number?",
        key="phone",
        required=False,
    )
    .read_textarea("What brings you here?", key="context")
    .read_multiple_choice(
        "How long would you like our call to be?",
        [{"label": "30 minutes", "value": 30}, {"label": "1 hour", "value": 60}],
        key="duration",
        initial_value=30,
    )
    .run("Next")
)

MEETING_TIME = timedelta(minutes=info["duration"])


# Check for available slots in host calendar and prompt user to select one
date_options = get_date_options(
    HOST_EMAILS,
    MEETING_TIME,
    MEETING_SPACING,
    GOAL_TIMEZONE,
    BROWSER_TIMEZONE,
    MIN_AVAILABLE_HOUR,
    MAX_AVAILABLE_HOUR,
)


# Add attendees to meeting
item = ListItemSchema().read_email("Email")
add_emails = (
    Page()
    .display("If you'd like to add other people to the chat, add their emails below.")
    .read_list(item, key="email", required=False)
    .run("Schedule")
)
additional_emails = add_emails["email"] or []


# Send meeting info to next stage
meeting_info = {
    "name": info["name"],
    "email": info["email"],
    "company": info["company"],
    "context": info["context"],
    "selected_slots": date_options["selected_slot"],
    "additional_emails": additional_emails,
}
set_data("meeting_info", meeting_info)


# Display confirmation message
display_markdown(
    """
## Your chat is scheduled!

Check your email for a calendar invite.

See you there 👋🏼
""",
    end_program=True,
)
