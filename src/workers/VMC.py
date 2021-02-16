from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multicondition import all_of, none_of

print(EC.presence_of_element_located)
print(all_of)

WHATSAPP_URL  = 'http://web.whatsapp.com'
PROFILE_PATH = r'C:\Users\Admin\AppData\Local\Google\Chrome\User Data\Profile 2'

#Popen(['chrome', '--remote-debugging-port=2131'])

# WhatsApp needs to be logged in
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--user-data-dir=AutoMate User Data')
options.add_argument('--profile-directory=Profile 2')

browser = webdriver.Chrome(options=options)
browser.get('https://web.whatsapp.com/')

# Wait for whatsapp to load in our initiating element
WebDriverWait(browser, 10).until(
    EC.all_of(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span[title='VMC OIC-2 batch 2022'")),
        EC.none_of(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#startup")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#initial-startup"))
        )
    )
)

source = browser.page_source
#soup = BeautifulSoup(source, 'html.parser')
group_name_element = browser.find_element_by_css_selector("span[title='VMC OIC-2 batch 2022'")
print(group_name_element)
# Figure out how to get to actual group div from the title='VMC OIC-2 batch 2022' span
# Figure out where to click
# Can we click?

input()
browser.quit()
