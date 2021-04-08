import os
import re

def get_info_from_link(source: str):
    solvedLink = re.search(r"(\d+)\?pwd=(\w+)", source)
    meeting_id = solvedLink.group(1)
    pwd = solvedLink.group(2)
    return meeting_id, pwd

def join_from_info(meeting_id: str, hashed_pwd: str):
    url = f"zoommtg://zoom.us/join?action=join&confno={meeting_id}&pwd={hashed_pwd}"
    command = f'%appdata%/Zoom/bin/zoom.exe --url="{url}" & exit'
    os.popen(command)

def join_from_link_source(source: str):
    meeting_id, pwd = get_info_from_link(source)
    join_from_info(meeting_id, pwd)