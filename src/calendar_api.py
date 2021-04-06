import os
from typing import Sequence, TextIO, Union, Optional, List, Dict, Type, Tuple, Int

from _io import TextIOWrapper # type: ignore
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

scopes = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events.readonly"
]

# API FUNCTIONS

def get_creds(scopes: Sequence[str], data_folder: Union[str, TextIO] = "data", show_auth_prompt: bool = True) -> Type[Credentials]:
    """Get/create user credentials in given folder with specified scopes.

    Args:
        scopes: The scopes listed in the OAuth consent screen.
        data_folder: The folder containing client_secret.json and to store credentials in.
        show_auth_prompt: Whether or not to show the user the authourization link in the console.

    Returns:
        The credentials stored or created.
    """
    # Convert data_folder to string if not already so
    if type(data_folder) == TextIOWrapper:
        data_folder = data_folder.name
    
    creds: Optional[Type[Credentials]] = None
    # The file token.json stores the user"s access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(data_folder+"\\token.json"):
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
def get_service() -> Resource:
    '''Construct or return a service for interacting with the Calendar v3 API

    Returns:
        A Resource object that can interact with the Calendar v3 API
    '''
    global service 
    if service is None:
        creds: Credentials = get_creds(scopes, data_folder="data", show_auth_prompt=False)
        service = build("calendar", "v3", credentials=creds)
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

def get_calendar_from_list_entry(calendar_list_entry: dict) -> str:
    '''Get the calendar from a calendarListEntry.

    Args:
        calendar_list_entry: A calendarListEntry dictionary from calendarList.items

    Returns:
        The calendar object associated with the given calendarListEntry's id.
    '''
    service = get_service()
    # calendarListEntry has partial, useless data and isn't
    # very useful in the API, directly getting calendar is 
    # more sensible
    calendar_id = calendar_list_entry["items"] 
    calendar = service.calendars().get(calendarId=calendar_id).execute() 
    return calendar

def get_events_in_time_span(calendar: Dict, time_from: datetime, time_to: datetime, allow_incomplete_overlaps: bool = False) -> List[Dict]:
    '''Get events partially and/or completely inside a time span from the given calendar.

    Args:
        calendar: A Calendar dictionary.
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
    events = service.events(calendarId=calendar["id"])
    if allow_incomplete_overlaps == False:
        # time_from and time_to can be directly set to timeMin and
        # timeMax but they have to be converted to string RFC3999.
        time_from = time_from.astimezone().isoformat() # RFC3999 requires the timezone
        time_to = time_to.astimezone().isoformat()

        events_in_span = events.list(
            timeMin=time_from, timeMax=time_to,
            singleEvents=True, orderBy="startTime" # startTime order requires singleEvents to be True
        ).execute()
        return events_in_span["items"] # Events are a level deeper
    else:
        # time_from and time_to can't be used to check partial overlaps
        # a day's span is used and filtering is done against time_from
        # and time_to later.
        first_day_start = datetime(year=time_from.year, month=time_from.month, day=time_from.day) # Accept spans of arbitary lengths
        last_day_end = datetime(year=time_to.year, month=time_to.month, day=time_to.day+1)

        events_today = events.list(
            timeMin=first_day_start, timeMax=last_day_end,
            singleEvents=True, orderBy="startTime"
        ).execute()
        events_today = events_today["items"]
        events_in_span = []
        for event in events_today:
            event_start = event["start"]["datetime"]
            event_end = event["start"]["datetime"]

            # Operators can be used with datetime objects
            event_start = datetime.fromisoformat(event_start)
            event_end = datetime.fromisoformat(event_end)

            event_starts_before = event_start < time_from
            event_ends_after = event_end > time_to

            if event_starts_before and not event_ends_after:
                # Cross only start time
                event["overlapType"] = "OverStart"
            elif not event_starts_before and event_ends_after:
                # Cross only end time
                event["OverlapType"] = "OverEnd"
            elif event_starts_before and event_ends_after:
                # Cross both start and end times
                event["OverlapType"] = "Across"
            elif not event_starts_before and not event_ends_after:
                # Starts and ends in timespan
                event["OverlapType"] = "Inside"
        return events_in_span


if __name__ == "__main__":
    result = get_calendar_list()
    teamie_calendar_list_entry = result[2]
    teamie_calendar = get_calendar_from_list_entry(teamie_calendar_list_entry)
    print(teamie_calendar)