from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import csv
import time

# Initialize Selenium WebDriver
driver = webdriver.Chrome()

# Function to solve CAPTCHA using 2Captcha
def solve_captcha(site_key, url):
    API_KEY = 'YOUR_2CAPTCHA_API_KEY'
    response = requests.get(f'http://2captcha.com/in.php?key={API_KEY}&method=userrecaptcha&googlekey={site_key}&pageurl={url}')
    request_id = response.text.split('|')[1]
    time.sleep(20)  # Wait for CAPTCHA to be solved
    response = requests.get(f'http://2captcha.com/res.php?key={API_KEY}&action=get&id={request_id}')
    while 'CAPCHA_NOT_READY' in response.text:
        time.sleep(10)
        response = requests.get(f'http://2captcha.com/res.php?key={API_KEY}&action=get&id={request_id}')
    captcha_solution = response.text.split('|')[1]
    return captcha_solution

# Navigate to the CAPTCHA-protected website
driver.get('https://example.com/captcha-protected-page')

# Solve CAPTCHA
site_key = 'SITE_KEY_FROM_WEBSITE'
captcha_solution = solve_captcha(site_key, driver.current_url)

# Submit CAPTCHA solution
captcha_input = driver.find_element(By.ID, 'g-recaptcha-response')
captcha_input.send_keys(captcha_solution)

# Click the submit button
submit_button = driver.find_element(By.ID, 'submit-button')
submit_button.click()

# Wait for the page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'data-element')))

# Extract data
data_elements = driver.find_elements(By.CLASS_NAME, 'data-class')
data = [element.text for element in data_elements]

# Save data to CSV
with open('data. - The generated text has been blocked by our content filters.