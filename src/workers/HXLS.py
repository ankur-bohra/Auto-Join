import os.path
import pickle

import util # type: ignore
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events.readonly']

def get_class():
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
            credentials = flow.run_local_server(port=0) # type: ignore
        
        with open('data/token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    
    # Apply credentials to build service
    service = build('calendar', 'v3', credentials=credentials)

    # Interact with API
    calendar_list = service.calendarList().list().execute() # type: ignore
    for calendar in calendar_list['items']:
        if calendar['summary'] != 'GGN LMS Calendar':
            # Get events in valid time period
            calendar_id = calendar['id']
            calendar = service.events().list( # type: ignore
                calendarId=calendar_id,
                timeMin = util.time.now(),
                timeMax = util.time.offset(minutes=1)).execute()
            
            # Cumulate zoom classes
            descriptions = []
            for event in calendar['items']:
                if 'zoom' in event['description']:
                    descriptions.append(event['description'])
            
            if len(descriptions) != 0:
                return descriptions.pop()

def join_class():
    description = get_class()
    util.zoom.join_from_link(description)

primary_action = join_class

if __name__ == '__main__':
    print(get_class())
