import os
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

WHATSAPP = 'http://web.whatsapp.com'
PROFILE_PATH = 'C:/Users/pbohr/AppData/Roaming/Mozilla/Firefox/Profiles/rvqzov3w.AutoMate'

# WhatsApp needs to be logged in
options = Options()
options.profile = PROFILE_PATH

service = Service('geckodriver')

driver = webdriver.Firefox(options=options, service=service)
driver.get(WHATSAPP)

# Wait for whatsapp to load in our initiating element
WebDriverWait(driver, 10).until(
    EC.all_of(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span[title='VMC OIC-2 batch 2022'")),
        EC.none_of(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#startup")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#initial-startup"))
        )
    )
)

# Get to the actual gruop
group_name_span = driver.find_element(By.CSS_SELECTOR,"span[title='VMC OIC-2 batch 2022'")
location = group_name_span.location
action = ActionChains(driver)
action.move_to_element(group_name_span).click().perform()

# Get all the messages
messages = driver.find_elements((By.CLASS_NAME, 'message-in'))

# Remove non zoom hyperlink messages
for message in messages:
    try:
        text_span = message.find_element((By.CSS_SELECTOR, 'span[dir=ltr]'))
        hyperlink = text_span.find_element((By.PARTIAL_LINK_TEXT, "zoom"))
        class_link = hyperlink.get_attribute('href')
    except:
        messages.remove(message)

# Pick most accurate class
next_class = None
for message in messages:
    text_span = message.find_element((By.CSS_SELECTOR, 'span[dir=ltr]'))
    text: str = text_span.text
    date_match = re.search(r'([a-zA-Z]+)\s(\d+)', text) # Format: 'Feb 18'
    time_match = re.search(r'(\d+):\d+', text) # Class longer than an hour, minutes not captured
    
    month = date_match.group(1)
    date = int(date_match.group(2))
    hour = int(time_match.group(1))

    closer = False
    if next_class is None:
        closer = True
    else:
        if month == next_class['time']['month']:
            if date < next_class['time']['date']: # Feb 13 over Feb 10
                closer = True
            elif date == next_class['time']:
                if hour < next_class['time']['hour']:
                    closer = True
        
    if closer:
        next_class = {
            'message': message,
            'date': date,
            'time' : {
                'month': month,
                'hour': hour
            }
        }


text_span = next_class['message'].find_element((By.CSS_SELECTOR, 'span[dir=ltr]'))
hyperlink = text_span.find_element((By.PARTIAL_LINK_TEXT, "zoom"))
class_link = hyperlink.get_attribute('href')
meeting_id = re.search(r'\d+', class_link).group()
pwd = re.search(r'pwd=(\w+)', class_link).group(1)

url = f'zoommtg://zoom.us/join?action=join&conference_id={meeting_id}&pwd={pwd}&uname=Ankur Bohra 9P22GG1010'
command = f'%appdata%/Zoom/bin/zoom --url="{url}" && exit'

os.popen(command)

driver.quit()