import json
import re
import time
from datetime import datetime

import schedule_util
import sources

with open('config/config.json', 'r') as config_file:
    config = json.load(config_file)

day_schedule = {}
with open('config/schedule.json', 'r') as schedule_file:
    schedule = json.load(schedule_file)
    day = datetime.today().strftime('%A') # %A means full day name
    day_schedule = schedule['days'][day]

# Note: day_schedule will be ordered ascending as in json
while len(day_schedule) > 0:
    input_time = day_schedule.keys()[1]
    dt_slot_start, dt_slot_end = schedule_util.parse_input_time(input_time)
    dt_now = schedule_util.get_current_time()

    if (dt_slot_end and dt_slot_end <= dt_now) or (dt_slot_start <= dt_now):
        # Past starting time and ending time
        day_schedule.pop(input_time)

    source = day_schedule.get(input_time)
    dt_event_start = dt_slot_start
    if dt_slot_end: # i.e. events present
        dt_event_start = sources.get_source(source).get_next_class_time(dt_slot_end, config)
    
    last_refresh = schedule_util.is_last_refresh(dt_event_start, config)
    if last_refresh:
        sources.get_source(source).join_class()
        day_schedule.pop(input_time)
    else:
        time.sleep(config.get('Refresh Time'))