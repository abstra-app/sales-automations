import json
import os
from datetime import timedelta, datetime
from typing import Dict, List
import pytz
from abstra.forms import Page
from dateutil.parser import parse as dt_parse
from urllib.parse import parse_qs, urlparse
from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.owned",
    "https://www.googleapis.com/auth/calendar.events.freebusy",
]


class DatetimeRange:
    def __init__(self, start, end):
        if not isinstance(start, datetime):
            raise Exception(
                f"start should be a datetime.datetime object, but it is {type(start)} instead"
            )
        if not isinstance(start, datetime):
            raise Exception(
                f"end should be a datetime.datetime object, but it is {type(end)} instead"
            )
        if not start.tzinfo:
            raise Exception("start should be timezone aware")
        if not end.tzinfo:
            raise Exception("end should be timezone aware")
        if start > end:
            raise Exception(f"start {start} should be smaller than end ({end})")

        self.start = start
        self.end = end

    def intersection(self, range2):
        if range2.start >= self.end or range2.end <= self.start:
            return None
        else:
            return DatetimeRange(
                max(self.start, range2.start), min(self.end, range2.end)
            )

    def slots(self, size, spacing):
        result = []
        # Starts from a fixed time
        time = self.start.replace(minute=0, second=0, microsecond=0)
        while time < self.end:
            start_time = time
            end_time = time + size
            if end_time > self.end:  # Do not add a slot that ends beyond the range
                break
            result.append(DatetimeRange(start_time, end_time))
            time = end_time

        return result

    def encode(self):
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
        }

    @staticmethod
    def decode(dict_repr):
        start = dt_parse(dict_repr.get("start", dict_repr.get("begin")))
        end = dt_parse(dict_repr["end"])
        return DatetimeRange(start, end)

    def __repr__(self):
        return f"datetime_range({self.start}, {self.end})"


def get_free_busy_hours(emails: List[str], work_range, timezone):
    all_busy_hours = []
    for email in emails:
        auth_json = os.getenv("GOOGLE_JSON")
        if auth_json is None:
            raise Exception("GOOGLE_JSON environment variable is not set")

        creds = service_account.Credentials.from_service_account_info(
            json.loads(auth_json)
        )
        creds = creds.with_scopes(SCOPES)
        creds = creds.with_subject(email)
        calendar = build("calendar", "v3", credentials=creds)

        body = {
            "timeMin": work_range.start.astimezone(pytz.UTC)
            .replace(tzinfo=None)
            .isoformat()
            + "Z",
            "timeMax": work_range.end.astimezone(pytz.UTC)
            .replace(tzinfo=None)
            .isoformat()
            + "Z",
            "timeZone": timezone.zone,
            "items": [{"id": email}],
        }

        busy_hours = [
            DatetimeRange(
                dt_parse(busy["start"]).astimezone(timezone),
                dt_parse(busy["end"]).astimezone(timezone),
            )
            for busy in calendar.freebusy()
            .query(body=body)
            .execute()["calendars"][email]["busy"]
        ]
        all_busy_hours.extend(busy_hours)
    return all_busy_hours


def schedule_event(
    ownerEmails: List[str],
    event_range,
    atendee: Dict[str, str],
    additionalEmails: List[Dict[str, str]] = [],
    timezone=pytz.timezone("America/Sao_Paulo"),
    context="",
    alternate_title=None,
):
    auth_json = os.getenv("GOOGLE_JSON")
    if auth_json is None:
        raise Exception("GOOGLE_JSON environment variable is not set")

    # Assume the first email in the list will be used to create the calendar event
    creds = service_account.Credentials.from_service_account_info(json.loads(auth_json))
    creds = creds.with_scopes(SCOPES)
    creds = creds.with_subject(ownerEmails[0])
    calendar = build("calendar", "v3", credentials=creds)

    # Create a list of attendee dict objects to include in event body
    attendees = [{"email": email} for email in ownerEmails]
    # Append additional attendee
    attendees.append({"email": atendee["email"]})
    if additionalEmails:
        for additionalEmail in additionalEmails:
            attendees.append({"email": additionalEmail["Email"]})

    summary = f'Meeting <> {atendee["name"]} - {atendee["company"]}'
    if alternate_title is not None:
        summary = alternate_title

    event = {
        "summary": summary,
        "description": context,
        "start": {
            "dateTime": event_range.start.isoformat(),
            "timeZone": timezone.zone,
        },
        "end": {
            "dateTime": event_range.end.isoformat(),
            "timeZone": timezone.zone,
        },
        "attendees": attendees,
        "conferenceData": {
            "createRequest": {
                "requestId": f"req-{event_range.start.isoformat()}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    resposta = (
        calendar.events()
        .insert(
            calendarId="primary", body=event, sendUpdates="all", conferenceDataVersion=1
        )
        .execute()
    )

    return resposta


def get_slot_label(slot, browser_timezone):
    start = slot.start.astimezone(browser_timezone)
    end = slot.end.astimezone(browser_timezone)
    return f"{start.strftime('%H:%M')} to {end.strftime('%H:%M')}"


def is_busy(busy_hours, slot, min_available_hour, max_available_hour):
    if any([slot.intersection(busy) for busy in busy_hours]):
        return "Busy"
    if slot.start.weekday() in [5, 6]:
        return "Not a weekday"
    if slot.start.time().hour < min_available_hour:
        return "Starting before work time"
    if slot.start.time().hour > max_available_hour:
        return "Starting after work time"
    if slot.end.time().hour >= max_available_hour:
        return "Ending after work time"
    return False


def get_date_options(
    emails: List[str],
    meeting_time,
    meeting_spacing,
    goal_timezone,
    browser_timezone,
    min_available_hour,
    max_available_hour,
):
    now = datetime.now(goal_timezone)

    # Populate object with possible slots
    work_range = DatetimeRange(timedelta(days=1) + now, timedelta(days=14) + now)

    busy_hours = get_free_busy_hours(emails, work_range, timezone=goal_timezone)

    work_slots = work_range.slots(meeting_time, meeting_spacing)

    options = [
        (slot.start.astimezone(browser_timezone), slot.end.astimezone(browser_timezone))
        for slot in work_slots
        if not is_busy(busy_hours, slot, min_available_hour, max_available_hour)
    ]

    page = (
        Page()
        .read_appointment(
            f"Pick a day for the meeting ({browser_timezone.zone})",
            slots=options,
            key="selected_slot",
        )
        .run()
    )

    return {
        "selected_slot": {
            "start": page["selected_slot"].begin.isoformat(),
            "end": page["selected_slot"].end.isoformat(),
        }
    }


def get_date_options_ptbr(
    emails: List[str],
    meeting_time,
    meeting_spacing,
    goal_timezone,
    browser_timezone,
    min_available_hour,
    max_available_hour,
):
    now = datetime.now(goal_timezone)

    # Populate object with possible slots
    work_range = DatetimeRange(timedelta(days=1) + now, timedelta(days=14) + now)

    busy_hours = get_free_busy_hours(emails, work_range, timezone=goal_timezone)

    work_slots = work_range.slots(meeting_time, meeting_spacing)

    options = [
        (slot.start.astimezone(browser_timezone), slot.end.astimezone(browser_timezone))
        for slot in work_slots
        if not is_busy(busy_hours, slot, min_available_hour, max_available_hour)
    ]

    page = (
        Page()
        .read_appointment(
            f"Escolha um horário ({browser_timezone.zone})",
            slots=options,
            key="selected_slot",
        )
        .run("Marcar")
    )

    return {
        "selected_slot": {
            "start": page["selected_slot"].begin.isoformat(),
            "end": page["selected_slot"].end.isoformat(),
        }
    }


def google_link(event: dict):
    html_link = event.get("htmlLink", "")
    ## dont use event.get("id") they have different meanings
    event_id = parse_qs(urlparse(html_link).query).get("eid", [""])[0]
    return f"https://calendar.google.com/calendar/u/0/r/eventedit/copy/{event_id}"


def meeting_link(event: dict):
    return event.get("hangoutLink", "")
