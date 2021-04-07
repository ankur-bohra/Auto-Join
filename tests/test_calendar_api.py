from datetime import datetime, timedelta

import pytest
from src import calendar_api


# Credentials
@pytest.fixture
def scopes():
    return ["https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events.readonly",
            "https://www.googleapis.com/auth/calendar.events"]

@pytest.fixture
def create_events():
    def _create_events(calendarId, events):
        # Create event
        service = calendar_api.get_service()
        ids = {}
        for event_data in events:
            event = {
                "summary": event_data.get("name"),
                "start": {"dateTime": event_data["start"].astimezone().isoformat()},
                "end": {"dateTime": event_data["end"].astimezone().isoformat()}
            }
            event = service.events().insert(calendarId=calendarId, body=event).execute()
            ids[event_data.get("name")] = event["id"]
        return ids
    return _create_events

@pytest.fixture
def delete_events():
    def _delete_events(ids):
        service = calendar_api.get_service()
        for _id in ids.values():
            print("Deleting", _id)
            service.events().delete(calendarId="primary", eventId=_id).execute()
    return _delete_events

class TestGetCreds:
    def test_without_folder(self, scopes):
        credentials = calendar_api.get_creds(scopes)
        assert credentials.valid

    def test_with_folder(self, scopes):
        credentials = calendar_api.get_creds(scopes, "data")
        assert credentials.valid

    def test_from_auth_file(self, scopes):
        credentials = calendar_api.get_creds(scopes)
        assert credentials.valid

    def test_without_auth_prompt(self, scopes, capsys):
        credentials = calendar_api.get_creds(scopes, reuse_creds=False, show_auth_prompt=False)
        output = capsys.readouterr()
        assert output.out == "\n"

class TestGetEventsInTimeSpan:
    def test_without_incomplete_overlaps(self, create_events, delete_events):
        span_start = datetime.now() + timedelta(minutes=3)
        span_end = span_start + timedelta(minutes=2)

        ids = create_events("primary", [
            {"name": "OverStart", "start": span_start - timedelta(seconds=30), "end": span_start + timedelta(seconds=30)},
            {"name": "OverEnd", "start": span_end - timedelta(seconds=30), "end": span_end + timedelta(seconds=30)},
            {"name": "Inside", "start": span_start + timedelta(seconds=30), "end": span_start + timedelta(seconds=30)},
            {"name": "Across", "start": span_start - timedelta(seconds=30), "end": span_end + timedelta(seconds=30)}
        ])
        events = calendar_api.get_events_in_time_span("primary", span_start, span_end)
        for event in events:
            assert event["overlapType"] == "Inside"
        delete_events(ids)

    def test_with_incomplete_overlaps(self, create_events, delete_events):
        span_start = datetime.now() + timedelta(minutes=3)
        span_end = span_start + timedelta(minutes=2)

        ids = create_events("primary", [
            {"name": "OverStart", "start": span_start - timedelta(seconds=30), "end": span_start + timedelta(seconds=30)},
            {"name": "OverEnd", "start": span_end - timedelta(seconds=30), "end": span_end + timedelta(seconds=30)},
            {"name": "Inside", "start": span_start + timedelta(seconds=30), "end": span_start + timedelta(seconds=30)},
            {"name": "Across", "start": span_start - timedelta(seconds=30), "end": span_end + timedelta(seconds=30)}
        ])
        events = calendar_api.get_events_in_time_span("primary", span_start, span_end)
        for event in events:
            assert event["id"] == ids[event["overlapType"]] # Check if overlap assignment is correct
        delete_events(ids)
