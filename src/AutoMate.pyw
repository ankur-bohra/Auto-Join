import json
import re
import time
from datetime import datetime

import workers

# ----------------------------------------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------------------------------------
# Values here are safe to edit

REFRESH_TIME = 50 # check if it's time to join every x seconds
# Note: REFRESH_TIME affects how early classes are joined.
#       Atleast one refresh will happen in REFRESH_TIME seconds before the class, so it is safest to say: 
#      'Classes will never be joined before REFRESH_TIME from the class'
#       e.g. REFRESH_TIME = 50 means classes will be joined anywhere** in the 50 seconds before the class
#
# **MIN_JOIN_TIME can change this so that classes are joined atleast some time before the class to allow manual
#   joining in case of a problem.

MIN_JOIN_TIME = 1 # join atleast before y seconds before the class begins
# ----------------------------------------------------------------------------------------------------------

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

day_schedule = {}
with open('data/schedule.json') as schedule_file:
    schedule = json.load(schedule_file)
    day = datetime.today().strftime('%A') # %A means full day name
    day_schedule = schedule.days[day]

sortedTimings = day_schedule.keys().sort(key=solveTime, reverse=True) # Earlier time first out
while len(day_schedule) > 0:
    target_time = sortedTimings[:-1]
    area = day_schedule[target_time]
    hr, mins = getTime()
    target_hr, target_mins, _ = parseTime(target_time)

    # Check if this is the last refresh in the join span
    last_refresh = True if mins + REFRESH_TIME < target_mins - MIN_JOIN_TIME else False
    if hr == target_hr and last_refresh:
        workers.execute_job(area)