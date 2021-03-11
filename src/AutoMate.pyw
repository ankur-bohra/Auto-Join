import json
import re
import time
from datetime import datetime

import sources

def parseTime(raw: str):
    # (H?)H:MM(AM/PM)
    solved = re.search(r'(\d+):(\d+)(\w+)', raw)
    hrs = solved.group(1)
    mins = solved.group(2)
    period = solved.group(3)
    return int(hrs), int(mins), period

def solveTime(raw: str):
    hrs, mins, period = parseTime(raw)
    solved = (12 if period == 'PM' else 0) + hrs + (mins/60)
    return solved

def getTime():
    now = datetime.now()
    hrs = now.strftime('%H')
    mins = now.strftime('%M')
    return int(hrs), int(mins)

config = None
with open('config/config.json', 'r') as config_file:
    config = json.load(config_file)

day_schedule = {}
with open('config/schedule.json', 'r') as schedule_file:
    schedule = json.load(schedule_file)
    day = datetime.today().strftime('%A') # %A means full day name
    day_schedule = schedule['days'][day]

sortedTimings = list(day_schedule.keys())
sortedTimings.sort(key=solveTime, reverse=True) # Earlier time first out
while len(day_schedule) > 0 and len(sortedTimings) > 0:
    target_time = sortedTimings[-1]
    source = day_schedule[target_time]
    hr, mins = getTime()
    target_hr, target_mins, _ = parseTime(target_time)

    if hr > target_hr or (hr == target_hr and mins > target_mins):
        sortedTimings.remove(target_time)
        day_schedule.pop(target_time)
        print('Cleared past:', target_time, source)
        continue
    print(sortedTimings)
    # Check if this is the last refresh in the join span
    last_refresh = True if mins + config.REFRESH_TIME/60 < target_mins - config.MIN_JOIN_TIME/60 else False
    if hr == target_hr and last_refresh:
        sources.get_source(source).join_link()