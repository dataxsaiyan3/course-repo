from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://create.microsoft.com/en-us/search?query=Resumes")

soup = BeautifulSoup(driver.page_source, 'html.parser')

links = soup.find_all('a')

cv_links = [link['href'] for link in links if 'resume' in link['href']]

# Download the Word examples
for link in cv_links[1:50]: # Download only the first 50 CVs
    # Navigate to the page
    driver.get('https://create.microsoft.com' + link)
    
    time.sleep(50)
    
    download_button = driver.find_element(By.XPATH, '//button[normalize-space()="Download"]')
    download_button.click()
    
    time.sleep(50)

driver.quit()