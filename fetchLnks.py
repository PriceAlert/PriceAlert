import json
import schedule
import time
from selenium import webdriver
from FetchData import go_to_product
from selenium.webdriver.common.by import By
from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import asyncio

async def main(category):
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get('https://www.amazon.in')
    browser.maximize_window()
    
    input_search = browser.find_element(By.ID, 'twotabsearchtextbox')
    search_button = browser.find_element(By.XPATH, "(//input[@type='submit'])[1]")
    
    search = category
    input_search.send_keys(search)
    sleep(1)
    search_button.click()
    
    lnks = browser.find_elements(By.TAG_NAME, "a")
    search_result = '&keywords='
    search_item = search.split(' ')
    
    for i, item in enumerate(search_item):
        search_result += item
        if i != len(search_item) - 1:
            search_result += '+'
    
    search_result += '&qid='
    lnks = [*set(lnks)]

    await go_to_product(lnks, search_result, search)

    browser.quit()

def job():
    with open('./inputs.json', 'r') as f:
        data = json.load(f)
        categories = data['Category']
        for category in categories:
            # Run the asynchronous code
            print(category)
            asyncio.run(main(category))

# Schedule the job to run every 12 hours
schedule.every(12).hours.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)