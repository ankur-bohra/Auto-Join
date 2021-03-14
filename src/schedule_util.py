import re
from datetime import datetime, timedelta

def parse_formatted_time(time_string):
    today = datetime.today().date()
    date_string = today.strftime('%d/%m/%y') + ' ' + time_string
    date = datetime.strptime(date_string, '%d/%m/%y %I:%M%p')
    return date.astimezone()

def parse_input_time(input_time):
    pattern = r'(\d+:\d+\w{2})(?:-(\d+:\d+\w{2}))?'
    match = re.search(pattern, input_time)
    
    time_start = match.group(1)
    dt_start = parse_formatted_time(time_start)
    result = (dt_start, None)

    time_end = match.group(2)
    if time_end:
        dt_end = parse_formatted_time(time_end)
        result = (dt_start, dt_end)
    return result

def get_current_time():
    dt = datetime.now()
    return dt.astimezone()

def is_last_refresh(dt_event, config):
    dt_now = get_current_time()
    dt_refresh = dt_now + timedelta(seconds=config.get('REFRESH_TIME'))
    dt_prejoin = dt_event - timedelta(seconds=config.get('PREJOIN_OFFSET'))

    return dt_refresh >= dt_prejoin