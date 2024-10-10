from abstra.workflows import get_data
import pytz
from calendar_utils import DatetimeRange, schedule_event

GOAL_TIMEZONE = pytz.timezone("America/Sao_Paulo")
HOST_EMAILS = ["sample@domain.com"]

meeting_info = get_data("meeting_info")

# Schedule calendar event
# Schedule Event on google calendar
atendee = {
    "name": meeting_info["name"],
    "email": meeting_info["email"],
    "company": meeting_info["company"],
}
event_range = DatetimeRange.decode(meeting_info["selected_slots"])
schedule_event(
    HOST_EMAILS,
    event_range,
    atendee,
    additionalEmails=meeting_info["additional_emails"],
    timezone=GOAL_TIMEZONE,
    context=f"Context: {meeting_info['context']}.",
)
