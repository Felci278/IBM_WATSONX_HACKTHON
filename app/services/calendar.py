"""
Service for scheduling donation/repair/upcycle events in Google Calendar.
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

# Google Calendar client
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")  # path to service account JSON


class CalendarServiceError(Exception):
    pass


def _get_calendar_service():
    """
    Authenticate and return Google Calendar API service.
    """
    if not GOOGLE_CREDENTIALS_FILE or not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        raise CalendarServiceError("Google Calendar credentials missing. Set GOOGLE_CALENDAR_CREDENTIALS in .env")

    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=credentials)
        return service
    except Exception as e:
        raise CalendarServiceError(f"Failed to authenticate: {e}")


def schedule_event(summary: str, description: str, start_time: Optional[datetime] = None, duration_minutes: int = 60):
    """
    Schedule an event in Google Calendar.
    Args:
        summary (str): Title of the event
        description (str): Description/details
        start_time (datetime, optional): Defaults to now + 1hr
        duration_minutes (int): Duration of event
    """
    service = _get_calendar_service()

    if not start_time:
        start_time = datetime.utcnow() + timedelta(hours=1)

    end_time = start_time + timedelta(minutes=duration_minutes)

    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time.isoformat() + "Z"},
        "end": {"dateTime": end_time.isoformat() + "Z"},
    }

    try:
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return {"status": "scheduled", "event_link": created_event.get("htmlLink")}
    except Exception as e:
        raise CalendarServiceError(f"Failed to schedule event: {e}")
