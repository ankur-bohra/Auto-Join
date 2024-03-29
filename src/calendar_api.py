import os
from typing import Sequence, Optional, List, Dict, Type

from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

scopes = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events.readonly",
    "https://www.googleapis.com/auth/calendar.events"
]

# API FUNCTIONS

def get_creds(scopes: Sequence[str], data_folder: str = "data",
              show_auth_prompt: bool = True, reuse_creds: bool = True) -> Type[Credentials]:
    """Get/create user credentials in given folder with specified scopes.

    Args:
        scopes: The scopes listed in the OAuth consent screen.
        data_folder: The folder containing client_secret.json and to store credentials in.
        show_auth_prompt: Whether or not to show the user the authourization link in the console.
        reuse_creds: Whether or not to use credentials from previous runs.

    Returns:
        The credentials stored or created.
    """    
    creds: Optional[Type[Credentials]] = None
    # The file token.json stores the user"s access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if reuse_creds and os.path.exists(data_folder+"\\token.json"):
        creds = Credentials.from_authorized_user_file(data_folder+"\\token.json", scopes)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                data_folder+"\\client_secret.json", scopes)
            if show_auth_prompt:
                creds = flow.run_local_server(port=0)
            else:
                creds = flow.run_local_server(port=0, authorization_prompt_message="")
        # Save the credentials for the next run
        with open(data_folder+"\\token.json", "w") as token:
            token.write(creds.to_json())
    return creds

# service will be built only once per run
service = None
def get_service(reuse_creds: bool = True) -> Resource:
    '''Construct or return a service for interacting with the Calendar v3 API

    Args:
        reuse_creds: Whether or not to use credentials from previous runs.

    Returns:
        A Resource object that can interact with the Calendar v3 API
    '''
    global service 
    if service is None:
        credentials: Credentials = get_creds(scopes, data_folder="data", show_auth_prompt=False, reuse_creds=reuse_creds)
        service = build("calendar", "v3", credentials=credentials)
    return service

# Separate function because this will be needed in the selection UI
def get_calendar_list() -> Resource:
    '''Get a calendar list's items with the first 100 calendars.

    Returns:
        A list of calendarListEntrys.
    '''
    service = get_service()
    calendar_list = service.calendarList().list().execute() # Default maxResults = 100 which is sufficient
    return calendar_list["items"]

def get_calendar_from_name(calendar_name: str) -> Optional[Dict]:
    '''Get the calendar associated with a given calendar name.

    Args:
        calendar_name: The name of the calendar.

    Returns:
        The calendar associated with the calendar name.
    '''
    service = get_service()
    calendars = get_calendar_list()
    for calendar in calendars:
        if calendar["summary"] == calendar_name:
            calendar_id = calendar["id"]
            calendar = service.calendars().get(calendarId=calendar_id).execute()
            return calendar

def get_events_in_time_span(calendarId: str, time_from: datetime, time_to: datetime, allow_incomplete_overlaps: bool = False) -> List[Dict]:
    '''Get events partially and/or completely inside a time span from the given calendar.

    Args:
        calendarId: calendarId of the calendar to search.
        time_from: The start of the time span (inclusve).
        time_to: The end of the time span (exclusive).
        allow_incomplete_overlaps: Whether to include events not completely inside the time span. Defaults to false. 

    Returns:
        A list of Events each with an added field "overlapType" of possible values:
            "Inside": The Event starts and ends inside the time span.
            "OverStart": The Event starts before and ends inside the time span.
            "OverEnd": The Event starts inside and ends after the time span 
            "Across": The Event starts before and ends after the time span.
    '''
    service = get_service()
    events = service.events()

    # Make dts timezone aware
    time_from = time_from.astimezone()
    time_to = time_to.astimezone()

    events_overlapping_in_span = events.list(
        calendarId=calendarId,
        timeMin=time_from.isoformat(), timeMax=time_to.isoformat(),
        singleEvents=True, orderBy="startTime" # startTime order requires singleEvents to be True
    ).execute()["items"]
    events_chosen = [] # "Sink" for events passing filter
    for event in events_overlapping_in_span:
        event_start = event["start"]["dateTime"]
        event_end = event["end"]["dateTime"]

        # Operators can be used with datetime objects
        event_start = datetime.fromisoformat(event_start)
        event_end = datetime.fromisoformat(event_end)

        event_starts_before = event_start < time_from
        event_ends_after = event_end > time_to

        if not event_starts_before and not event_ends_after:
            event["overlapType"] = "Inside"
        elif allow_incomplete_overlaps:
            # Allow further divisions
            if event_starts_before and not event_ends_after:
                # Cross only start time
                event["overlapType"] = "OverStart"
            elif not event_starts_before and event_ends_after:
                # Cross only end time
                event["overlapType"] = "OverEnd"
            elif event_starts_before and event_ends_after:
                # Cross both start and end times
                event["overlapType"] = "Across"
        # else:
            # No overlapType assigned as only Inside is allowed and event wasn't inside
        
        if "overlapType" in event: # Event passed appropriate filter
            events_chosen.append(event)

    return events_chosen

if __name__ == "__main__":
    teamie_calendar = get_calendar_from_name("GGN LMS Calendar")
    print(teamie_calendar)