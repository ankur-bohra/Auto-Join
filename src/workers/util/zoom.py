import os
import re

def get_info_from_link(linkContainingString: str):
    meeting_id = re.search(r'\d+', linkContainingString).group()
    pwd = re.search(r'pwd=(\w+)', linkContainingString).group(1)
    return meeting_id, pwd

def join_from_info(meeting_id: str, hashed_pwd: str):
    url = f'zoommtg://zoom.us/join?action=join&confno={meeting_id}&pwd={hashed_pwd}'
    command = f'%appdata%/Zoom/bin/zoom.exe --url="{url}" & exit'
    os.popen(command)

def join_from_link(linkContainingString: str):
    meeting_id, pwd = get_info_from_link(linkContainingString)
    join_from_info(meeting_id, pwd)