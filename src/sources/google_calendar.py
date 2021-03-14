import json
import os.path
import pickle

from six import class_types

if __name__ == '__main__':
    import util  # type: ignore
else:
    from . import util

from datetime import datetime

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events.readonly']

classes_cache = None
last_lookup = datetime.now().astimezone()
def get_classes(slot_end):
    global classes_cache

    # Verify credentials
    credentials = None
    if os.path.exists('data/token.pickle'):
        with open('data/token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials = credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'data/client_secrets.json',
                SCOPES)
            credentials = flow.run_local_server(port=2131) # type: ignore
        
        with open('data/token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    # Get the target calendar
    with open('config/config.json') as config_file:
        config = json.load(config_file)
        target_calendar = config.get('Calendar Name')

    # Apply credentials to build service
    service = build('calendar', 'v3', credentials=credentials)

    # Interact with API
    calendar_list = service.calendarList().list().execute() # type: ignore
    for calendar in calendar_list['items']:
        if calendar['summary'] == target_calendar:
            # Get events in valid time period
            calendar_id = calendar['id']
            calendar = service.events().list( # type: ignore
                    calendarId = calendar_id,
                    timeMin = datetime.now().astimezone().isoformat('T'),
                    timeMax = slot_end.isoformat('T')
                ).execute()

            # Cumulate zoom links
            classes = []
            for event in calendar['items']:
                if 'zoom' in event['description']:
                    classes.append(event)

            classes_cache = classes

def get_next_class_time(dt_slot_end, config):
    global classes_cache
    if classes_cache:
        dt_now = datetime.now().astimezone()
        difference = dt_now - last_lookup
        if difference.seconds >= config.get('Calendar Cache Refresh Time'):
            classes_cache = get_classes(dt_slot_end)
    else:
        classes_cache = get_classes(dt_slot_end)

    classes_cache.sort(
        key = lambda event: datetime.fromisoformat(event.get('start').get('dateTime')),
        reverse = True
    )
    
    dt_next_class = classes_cache[-1]
    return dt_next_class

def join_class():
    global classes_cache
    next_class = classes_cache.pop()
    description = next_class['description']
    util.zoom.join_from_link(description)    

if __name__ == '__main__':
    join_class()
