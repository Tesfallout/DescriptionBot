import csv
import os
import re
import requests
import shutil
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


##### Scraping #####


baseUrl = "https://hianime.to/filter?type=2&status=2&language=1&sort=default&page="

pageNum = 1
lastPage = 0
morePages = True

main_links = {}  # Dictionary to store URL as key and a dictionary with title, state, and tag as value
page_links = set()

try:
    while morePages:
        # Set up Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode (no browser window)
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
                
        # Load the webpage
        driver.get(baseUrl + str(pageNum))
        driver.implicitly_wait(10)  # Wait up to 10 seconds

        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find all show links and titles (assuming they are inside anchor tags with a specific class or structure)
        show_elements = soup.find_all("a", href=True)
        
        page_pattern = re.compile(r".*page=(\d+)$")
        pattern = re.compile(r".*(-\d+$)")
        exclude_link = "https://hianime.to/az-list/0-9"  # Link to exclude
                        
        for link in show_elements:
            href = link.get("href")
            title = link.get("data-jname")  # Get the title from the data-jname attribute         

            if href and href != exclude_link:
                if pattern.match(href):
                    href = href.replace("https://hianime.to/", "https://hianime.to/watch/")
                    if title:  # Add to the dictionary if title exists

                        ### Character Cleanup ###
                        title = title.replace(",","")
                        title = title.replace("\"","")
                        title = title.replace("é","e")
                        title = title.replace("Ã—","x")
                        title = title.replace("♡","")
                        title = title.replace("â™¡","")
                        title = title.replace("è","e")
                        title = title.replace("Ã¨","e")
                        title = title.replace("â˜†","")
                        title = title.replace("☆","")

                        main_links[href] = {
                            "title": title,
                            "state": 0,  # Set state to 0
                            "tag": "tag"  # Set tag to "tag"
                        }
                if page_pattern.match(href):
                    page_links.add(href)
                                
        for page in page_links:  # Let this run every time a page is run, just in case not all are shown on the 1st page
            tempNum = page.split('=')[-1]
            if int(lastPage) < int(tempNum):
                lastPage = tempNum
             
        # Close the browser
        driver.quit()
                    
        pageNum += 1
        if int(pageNum) > int(lastPage):
            morePages = False

    # Sort the main_links dictionary by the title
    sorted_links = sorted(main_links.items(), key=lambda x: x[1]["title"])

    # Export the sorted data to a CSV file without the header
    with open('anime_data_new.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for url, data in sorted_links:
            writer.writerow([url, data["title"], data["state"], data["tag"]])
            

except Exception as e:
    print(f"An error occurred while scraping links: {e}")


##### Database Checking and Handling #####

# Check Status of Files
fileStatus = 1000
if os.path.exists('anime_data.csv'):
    fileStatus += 100

if os.path.exists('anime_data_old.csv'):
    fileStatus += 10

if os.path.exists('anime_data.bak'):
    fileStatus += 1
    

##### Handle File Statuses #####
    

if fileStatus == 1000 : #No Files Present
    with open('anime_data.csv','w',encoding='utf-8') as file:
        pass
    fileStatus += 1000

elif fileStatus == 1001 : #Only Backup Present
    shutil.copy('anime_data.bak','anime_data.csv')
    fileStatus += 100

elif fileStatus == 1010 : #Only _old Present
    shutil.move('anime_data_old.csv','anime_data.csv')
    fileStatus += 100
    fileStatus -=10

elif fileStatus == 1011 : #Backup and _old
    shutil.move('anime_data_old.csv','anime_data.csv')
    fileStatus += 100
    fileStatus -=10

elif fileStatus == 1111 : #Data Backup and _old
    os.remove('anime_data_old.csv')
    fileStatus -=10

if fileStatus == 1101 : #Data and Backup
    os.remove('anime_data.bak')
    shutil.copy('anime_data.csv','anime_data.bak')

elif fileStatus == 1100 : #Data Only
    shutil.copy('anime_data.csv','anime_data.bak')
    fileStatus += 1


##### .csv Handling #####


new_data = {}
old_data = {}


try:
    shutil.move("anime_data.csv", "anime_data_old.csv")
except FileNotFoundError:
    print("anime_data.csv not found")

    
with open("anime_data_new.csv", mode='r', encoding='utf-8') as new_csv:
    reader = csv.reader(new_csv)
    for row in reader:
        identifier = row[0]
        new_data[identifier] = row


with open("anime_data_old.csv", mode='r', encoding='utf-8') as old_csv:
    reader = csv.reader(old_csv)
    for row in reader:
        identifier = row[0]
        old_data[identifier] = row


merged_data = {}
for identifier, row in old_data.items():
    if identifier in new_data:
        # If identifier is in both, keep old_data row
        merged_data[identifier] = row
    elif row[2] != "D":
        # If identifier is only in old_data and third column is not "D", keep it
        merged_data[identifier] = row

for identifier, row in new_data.items():
    if identifier not in old_data:
        # If identifier is only in new_data, keep it
        merged_data[identifier] = row

# Write merged data to anime_data.csv
with open("anime_data.csv", mode='w', encoding='utf-8', newline='') as output_csv:
    writer = csv.writer(output_csv)
    for row in merged_data.values():
        writer.writerow(row)



os.remove('anime_data_old.csv')
os.remove('anime_data_new.csv')







        
