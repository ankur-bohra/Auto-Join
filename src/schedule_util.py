import re
import time
from datetime import datetime

def parse_formatted_time(raw: str):
    # (H?)H:MM(AM/PM)
    solved = re.search(r'(\d+):(\d+)(\w+)', raw)
    hrs = int(solved.group(1))
    mins = int(solved.group(2))
    period = solved.group(3)

    if period == 'PM':
        hrs += 12
    return hrs, mins

def solve_formatted_time(raw: str):
    hrs, mins = parse_formatted_time(raw)
    solved = hrs + (mins/60)
    return solved

def get_current_time():
    now = datetime.now()
    hrs = now.strftime('%H')
    mins = now.strftime('%M')
    secs = now.strftime('%S')
    return int(hrs), int(mins), int(secs)

def is_last_refresh(raw_time: str, refresh_time: int, min_prejoin_offset: int):
    hrs_now, mins_now, secs_now = get_current_time()
    hrs_event, mins_event = parse_formatted_time(raw_time)

    # Adjust mins_now to fractional minutes
    mins_now += secs_now/60

    # Calculate next refresh time
    hrs_next = hrs_now
    mins_next = mins_now + refresh_time/60
    if mins_next >= 60: # Update hour        
        mins_next -= 60
        hrs_next += 1
    next_refresh = hrs_next + mins_next/60

    # Set prejoin time
    hrs_prejoin = hrs_event
    mins_prejoin = mins_event - min_prejoin_offset/60
    if mins_prejoin < 0: # Udpate hour
        mins_prejoin += 60
        hrs_prejoin -= 1
    prejoin_time = hrs_prejoin + mins_prejoin/60

    # Finally compare next refresh time and prejoin time
    if next_refresh >= prejoin_time:
        print(f'{hrs_next}:{mins_next} comes AFTER {hrs_prejoin}:{mins_prejoin}')
        print(f'{next_refresh} >= {prejoin_time}')
        return True
    else:
        return False