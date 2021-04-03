import os
from typing import Sequence, TextIO, Union, Optional

from _io import TextIOWrapper # type: ignore
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

scopes = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events.readonly"
]

def get_creds(scopes: Sequence[str], data_folder: Union[str, TextIO] = "data", show_auth_prompt: bool = True) -> Credentials:
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

    creds: Optional[Credentials] = None
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

def get_calendar_list():
    service: Resource = get_service()
    calendar_list = service.calendarList().list().execute() # Default maxResults = 100 which is sufficient
    return calendar_list.get("items")

if __name__ == "__main__":
    print(get_calendar_list())