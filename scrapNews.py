from selenium import webdriver
import time
from bs4 import BeautifulSoup
import requests
import json

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome('chromedriver.exe', options=options)
baseURL = 'https://in.finance.yahoo.com'

driver.get(f'{baseURL}/quote/TATAMOTORS.NS/?p=TATAMOTORS.NS')
SCROLL_PAUSE_TIME = 1

# Get scroll height
last_height = driver.execute_script('return document.getElementById(\'render-target-default\').scrollHeight')

while True:
    # Scroll down to bottom
    driver.execute_script('window.scrollTo(0, document.getElementById(\'render-target-default\').scrollHeight);')

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script('return document.getElementById(\'render-target-default\').scrollHeight')
    print(new_height)
    if new_height == last_height:
        break
    last_height = new_height
page_source = driver.page_source

soup = BeautifulSoup(page_source)

d = soup.select('div#quoteNewsStream-0-Stream-Proxy li')
links = []
# print(d)
for i in d:
    try:
        links.append(i.select('a')[0].attrs['href'])
    except:
        pass

data = []
for i in links:
    r = None
    try:
        r = requests.get(i) if i.startswith('http') else requests.get(baseURL + i)
    except:
        time.sleep(5)
        r = requests.get(i) if i.startswith('http') else requests.get(baseURL + i)
    s = BeautifulSoup(r.content)
    q = {}
    try:
        q['time'] = s.select('time')[0].attrs['datetime']
        q['title'] = s.select('#SideTop-0-HeadComponentTitle > h1')[0].contents[0]
        q['text'] = ""
        for j in s.select('#Col1-0-ContentCanvas > article > div')[0].select('p'):
            v = j.contents[0]
            if v.name == None:
                q["text"] += v.__str__()
        data.append(q)
    except:
        continue

json.dump(data, open('data.json', 'w'))