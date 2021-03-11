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

sortedTimings = list(day_schedule.keys())
sortedTimings.sort(key=schedule_util.solve_formatted_time, reverse=True) # Earlier time first out
while len(day_schedule) > 0 and len(sortedTimings) > 0:
    target_time = sortedTimings[-1]
    source = day_schedule[target_time]

    hr, mins, secs = schedule_util.get_current_time()
    mins += secs/60 # Make directly mins comparable
    target_hr, target_mins = schedule_util.parse_formatted_time(target_time)
    if hr > target_hr or (hr == target_hr and mins >= target_mins):
        sortedTimings.remove(target_time)
        day_schedule.pop(target_time)
        continue

    # Check if this is the last refresh in the join span
    last_refresh = schedule_util.is_last_refresh(target_time, config['REFRESH_TIME'], config['MIN_PREJOIN_OFFSET'])
    if last_refresh:
        print('LAST REFRESH FOR', target_time)
        sources.get_source(source).join_link()
        sortedTimings.remove(target_time)
        day_schedule.pop(target_time)
        print('     COMPLETED TASK')
    else:
        time.sleep(config['REFRESH_TIME'])