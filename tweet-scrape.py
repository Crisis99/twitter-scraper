import csv
import keyring
from getpass import getpass
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

#this block of code allows us to enter our username and Password into the browser
#without us needing to write down our sensitive information in our code
if keyring.get_password("test","username"):
    print("Username and Password already saved")
else:
    username = input("Enter username:")
    sleep(10)
    password = getpass()
    sleep(10)
    keyring.set_password("test", "username",  username)
    keyring.set_password("test", "password",  password)

#credential manager
username = keyring.get_password("test", "username")
password = keyring.get_password("test", "password")

#get the person's username and tweet text
#catch exceptions (some tweets do not like being scraped for some reason)
def getTweets(box):
    try:
        username = box.find_element_by_xpath('.//span').text
    except exceptions.NoSuchElementException:
        username = ""
    try:
        text = box.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    except exceptions.NoSuchElementException:
        text = ""

    tweet = (username, text)
    return tweet

#open twitter
driver.get('https://www.twitter.com/login')
sleep(5)

#get username and pass
#enter username into username box
userbox = driver.find_element_by_name('session[username_or_email]')
userbox.clear()
userbox.send_keys(username)

#enter password into password box
passbox = driver.find_element_by_name('session[password]')
passbox.clear()
passbox.send_keys(password)

#click login
login = driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div[2]/form/div/div[3]/div/div')
sleep(2)
login.click()

#open advanced search
driver.get('https://twitter.com/search-advanced?lang=en')
sleep(5)

#select from december 1st 2020
fmonth = Select(driver.find_element_by_id('Month'))
fmonth.select_by_visible_text('December')
fday = Select(driver.find_element_by_id('Day'))
fday.select_by_visible_text('1')
fyear = Select(driver.find_element_by_id('Year'))
fyear.select_by_visible_text('2020')

#select to jan 1st 2020
tmonth = Select(driver.find_element_by_xpath('(//*[@id="Month"])[2]'))
tmonth.select_by_visible_text('January')
tday = Select(driver.find_element_by_xpath('(//*[@id="Day"])[2]'))
tday.select_by_visible_text('1')
tyear = Select(driver.find_element_by_xpath('(//*[@id="Year"])[2]'))
tyear.select_by_visible_text('2021')

#search exact phrase (this searches for "air pollution ?")
searchbox = driver.find_element_by_name('thisExactPhrase')
searchbox.send_keys('"air pollution ?"')
searchbox.send_keys(Keys.RETURN)
sleep(2)
#search latest tweets
driver.find_element_by_link_text('Latest').click()
sleep(2)

#get all tweets on the page
tweet_info = []
tweet_ids = set()
lastPos = driver.execute_script("return window.pageYOffset;")
scrolling = True

#while scrolling, get tweets
while scrolling:
    tweet_page = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    for box in tweet_page[-15:]:
        tweet = getTweets(box)

        #this is so we dont scrape the same tweet by accident
        if tweet:
            tweet_id = ''.join(tweet)
            if tweet_id not in tweet_ids:
                tweet_ids.add(tweet_id)
                tweet_info.append(tweet)

    #scroll down
    tryScroll = 0
    while True:
        #scroll position
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(2)
        currentPos = driver.execute_script("return window.pageYOffset;")
        if lastPos == currentPos:
            tryScroll += 1
            if tryScroll >= 3:
                scrolling = False
                break
            else:
                sleep(2)
        else:
            lastPos = currentPos
            break

#close webdriver when done
driver.close()

#write to spreadsheet
with open('tweets.csv', 'w', newline='', encoding='utf-8') as f:
    header = ['Username', 'Tweet text']
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(tweet_info)
