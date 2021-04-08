from datetime import datetime, timedelta

from . import calendar_api, zoom, ui

config = {}

cache = []
next_refresh = None
def get_events(use_cache=True):
    global config, cache, next_refresh
    now = datetime.now().astimezone()
    if now >= next_refresh or use_cache == False:
        next_refresh = now + timedelta(seconds=config["calendar"]["cache_refresh"])
        cache = calendar_api.get_events_in_time_span(now, next_refresh, allow_incomplete_overlaps=True)
    return cache

def get_current_event():
    events = get_events()

    with open("data/history.txt", "r") as stored_event:
        last_event = stored_event.read()

    possibilities = []
    now = datetime.now().astimezone()
    for event in events:
        if "zoom.us" not in event["description"].lower():
            continue
        event_start = datetime.fromisoformat(event["start"]["dateTime"])
        event_end = datetime.fromisoformat(event["end"]["dateTime"])
        if event["id"] != last_event and (event_start <= now <= event_end or event_start <= next_refresh):
            possibilities.append(event)

    if len(possibilities) > 0:
        if len(possibilities) > 1:
            ui.flag_conflicts(possibilities)
        # Join event
        event = possibilities.pop()
        zoom.join_from_link_source(event["description"])