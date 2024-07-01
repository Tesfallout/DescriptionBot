import csv
import datetime
import os
import re
import shutil
import time
import subprocess
import pyautogui
import pyperclip

from bs4 import BeautifulSoup

from selenium import webdriver


debug = True

def get_anime_season():
    now = datetime.datetime.now()
    month = now.month
    year = now.year

    if 1<= month <= 3:
        season = 'winter'
    elif 4 <= month <= 6:
        season = 'spring'
    elif 7 <= month <= 9:
        season = 'summer'
    elif 10 <= month <= 12:
        season = 'fall'
    else:
        print("Season Error")

    return season, year

def get_last_season(season, year):
    last_season = ""
    last_season_year = year

    if season == "winter":
        last_season = "fall"
        last_season_year = year-1
    elif season == "spring":
        last_season = "winter"
    elif season == "summer":
        last_season = "spring"
    elif season == "fall":
        last_season = "summer"

    return last_season, last_season_year

def get_html_content(url):

    chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

    window_size = "800,600"
    window_position = "100,100"
    
    command = [chrome_path, "--window-size=" + window_size, "--window-position=" + window_position, url]
    subprocess.Popen(command)
    time.sleep(3)
    pyautogui.moveTo(150, 300)
    pyautogui.rightClick()
    pyautogui.press('up')
    pyautogui.press('up')
    pyautogui.press('enter')
    time.sleep(1.25)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')
    response = pyperclip.paste()
    pyautogui.hotkey('alt', 'f4')
    
    #print(response)
    return response


def extract_show_info(html_content,season,year):
    temp_info_table = []

    soup = BeautifulSoup(html_content, 'html.parser')
    shows = soup.find_all('div', class_='item')

    for show in shows:
        show_info = {}

        a_tag = show.select_one('.name.d-title')
        sub_status = show.select_one('.ep-status.sub span')
        total_status = show.select_one('.ep-status.total span')
        a_href = show.select_one('.name.d-title')
        watched_placeholder = 0
        comment_placeholder = ""
        
        if a_tag:
            data_jp = a_tag.get('data-jp', '').strip()
            if data_jp:  # Skip if data-jp is an empty string
                show_info['data-jp'] = data_jp.replace(",","") #Removes commas in titles of shows
            else:
                show_info['data-jp'] = 'N/A'
        
        if sub_status:
            show_info['ep-status sub'] = sub_status.get_text(strip=True)
        else:
            show_info['ep-status sub'] = 'N/A'

        if total_status:
            show_info['ep-status total'] = total_status.get_text(strip=True)
        else:
            show_info['ep-status total'] = 'N/A'

        show_info['watched_placeholder'] = watched_placeholder
        show_info['comment_placeholder'] = comment_placeholder

        if a_href:
            href = a_href.get('href', '').strip()
            if href:
                show_info['href'] = href
            else:
                show_info['href'] = 'N/A'
        show_info['season'] = str(season)+"-"+str(year)

        temp_info_table.append(show_info)

    return temp_info_table


###### Main ######
    
current_season, current_year = get_anime_season()
last_season, last_season_year = get_last_season(current_season, current_year)
baseUrl = "https://aniwave.to/filter?keyword=&country%5B%5D=120822&season%5B%5D=" + str(current_season) + "&year%5B%5D=" + str(current_year) + "&type%5B%5D=tv&sort=recently_updated"
lastUrl = "https://aniwave.to/filter?keyword=&country%5B%5D=120822&season%5B%5D=" + str(last_season) + "&year%5B%5D=" + str(last_season_year) + "&type%5B%5D=tv&sort=recently_updated"

#### Crash Handling Database Recovery ####

if os.path.exists('anime_data.csv') and not os.path.exists('anime_data.bak'): # data is there, backup missing, backup data
    shutil.copy('anime_data.csv', 'anime_data.bak')
    print("Debug: data is there, backup missing, backup data")
    
elif not os.path.exists('anime_data.csv') and os.path.exists('anime_data.bak'): # data gone, restore from backup
    shutil.copy('anime_data.bak', 'anime_data.csv')
    print("Debug: data gone, restore from backup")

elif not os.path.exists('anime_data.csv') and os.path.exists('anime_data_old.csv'): # data gone, backup gone, restore from old, create backup
    shutil.copy('anime_data_old.csv', 'anime_data.csv')
    shutil.copy('anime_data.csv', 'anime_data.bak')
    print("Debug: data gone, backup gone, restore from old, create backup")
elif not os.path.exists('anime_data.csv') and not os.path.exists('anime_data.bak'): # starting from scratch, create data
    try:
        with open('anime_data.csv', 'w'):
            print("Debug: starting from scratch, create data")
            pass
    except Exception as e:
        pass
    
## Create redundant backups ##
    
if os.path.exists('anime_data.bak4'):
    shutil.copy('anime_data.bak4', 'anime_data.bak5')
if os.path.exists('anime_data.bak3'):
    shutil.copy('anime_data.bak3', 'anime_data.bak4')
if os.path.exists('anime_data.bak2'):
    shutil.copy('anime_data.bak2', 'anime_data.bak3')
if os.path.exists('anime_data.bak'):
    shutil.copy('anime_data.bak', 'anime_data.bak2')

try:
    os.remove('anime_data_old.csv')
    os.remove('anime_data_new.csv')
except OSError as e:
    pass

#### Rename Data to Old ####

try:
    shutil.move('anime_data.csv', 'anime_data_old.csv')
except FileNotFoundError:
    print("Debug: FileNotFoundError with anime_data.csv")
    pass
except PermissionError:
    print("Debug: PermissionError with anime_data.csv")
    pass
    
#### Get Current Season ####

if debug == True:print(baseUrl)

show_info_table = []
html_content = get_html_content(baseUrl)

if html_content:
    if debug == True:print(html_content)
    soup = BeautifulSoup(html_content, 'html.parser')
    page_numbers = re.findall(r'page=\d+', soup.prettify())
    show_info_table = extract_show_info(html_content,current_season,current_year) # add page 1 info to table

    totalPages = 1
    if page_numbers: # Find how many pages there are
        for page_number in page_numbers:
            pageInt = int(page_number.split('=')[1])
            if pageInt > totalPages:
                totalPages = pageInt

    pageUrl = baseUrl
    if debug == True:print(f"pageUrl : {pageUrl}")
    currentPage = 1
    while totalPages > currentPage:
        if debug == True:print(f"currentPage: {currentPage}")
        pageUrl = baseUrl + "&page=" + str(currentPage + 1)
        currentPage += 1
        html_content = get_html_content(pageUrl)
        soup = BeautifulSoup(html_content, 'html.parser')
            
        show_info_table += extract_show_info(html_content,current_season,current_year) # add page 2+ info to table

#### Get Last Season ####
            
html_content = get_html_content(lastUrl)

if html_content:
    soup = BeautifulSoup(html_content, 'html.parser')
    page_numbers = re.findall(r'page=\d+', soup.prettify())        
    show_info_table += extract_show_info(html_content,last_season,last_season_year) # add previous season page 1 info to table

    if page_numbers: # Find how many pages there are
        totalPages = 1
        for page_number in page_numbers:
            pageInt = int(page_number.split('=')[1])
            if pageInt > totalPages:
                totalPages = pageInt

    pageUrl = lastUrl
    currentPage = 1
    while totalPages > currentPage:
        pageUrl = lastUrl + "&page=" + str(currentPage + 1)
        currentPage += 1
        html_content = get_html_content(pageUrl)
        soup = BeautifulSoup(html_content, 'html.parser')
            
        show_info_table += extract_show_info(html_content,last_season,last_season_year) # add previous season page 2+ info to table

    if debug == True:
        print("show_info_table:")
        print(show_info_table)

if show_info_table:
    sorted_data = sorted(show_info_table, key=lambda x: x['data-jp'])
    with open('anime_data_new.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['data-jp', 'ep-status sub', 'ep-status total', 'watched_placeholder', 'comment_placeholder', 'href', 'season']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        for row in sorted_data:
            writer.writerow(row)
    

#### Data Combining ####

old_title = []      #0
old_aired = []      #1
old_airing = []     #2
old_watched = []    #3
old_comment = []    #4
old_url = []        #5
old_season = []     #6
old_info = [old_title,old_aired,old_airing,old_watched,old_comment,old_url,old_season]

new_title = []      #0
new_aired = []      #1
new_airing = []     #2
new_watched = []    #3
new_comment = []    #4
new_url = []        #5
new_season = []     #6
new_info = [new_title,new_aired,new_airing,new_watched,new_comment,new_url,new_season]

output_list = []

## Importing the old file ##

with open('anime_data_old.csv', 'r', newline='') as csv_old:
    csv_reader_old = csv.reader(csv_old)

    for row in csv_reader_old:
        skip = False
        aired = str(row).split(',')[-6][2:-1]
        airing = str(row).split(',')[-5][2:-1]
        watched = str(row).split(',')[-4][2:-1]
        season = str(row).split(',')[-1][2:-2]

        if debug == True :print(f"row in csv_reader_old : {row}")

        if "N/A" in (str(row).split(',')[-7])[2:-1]: # conditions to omit a line from the old file
            skip = True
            
        if season.split('-')[0] == current_season:
            skip == False
        elif season.split('-')[0] == last_season:
            if aired == airing and watched == "D":
                skip = True
            elif aired == airing:
                if watched.isdigit():
                    if not int(watched) > 0: #on a separate line to avoid typing mismatch with watched variable
                        skip = True
        elif season.split('-')[0] != last_season:
            if not watched.isdigit() or watched == aired:
                skip = True

        if "-E" in str(row):
            if airing.split('-')[1] == "E" and watched == "D":
                skip = True

        if skip == False:
            temp = len(str(row).split(',')) # handles extra commas in the show title
            if temp == 7:
                old_title.append((str(row).split(',')[-7])[2:-1].replace("Ã—","x")) # title
            elif temp == 8:
                old_title.append((str(row).split(',')[-8] + str(row).split(',')[-7])[2:-1].replace("Ã—","x"))
            elif temp == 9:
                old_title.append((str(row).split(',')[-9]+ str(row).split(',')[-8] + str(row).split(',')[-7])[2:-1].replace("Ã—","x"))
            old_aired.append(aired)                             # aired
            old_airing.append(airing)                           # airing
            old_watched.append(watched)                         # watched
            old_comment.append(str(row).split(',')[-3][2:-1])   # comment
            old_url.append(str(row).split(',')[-2][2:-1])       # url
            old_season.append(season)                           # season

    ## Importing the new file ##
            
    with open('anime_data_new.csv', 'r', newline='') as csv_new:
        csv_reader_new = csv.reader(csv_new)

        for row in csv_reader_new:
            skip = False
            aired = str(row).split(',')[-6][2:-1]
            airing = str(row).split(',')[-5][2:-1]
            watched = str(row).split(',')[-4][2:-1]
            season = str(row).split(',')[-1][2:-2]

            if debug == True:print(f"row in csv_reader_new : {row}")

            if "N/A" in (str(row).split(',')[-7])[2:-1]: # conditions to omit a line from the new file
                skip = True
            if season.split('-')[0] == current_season:
                skip == False
            elif season.split('-')[0] == last_season:
                if aired == airing:
                    skip = True
            else:
                skip = True

            if skip == False:                  
                new_title.append((str(row).split(',')[-7])[2:-1].replace("Ã—","x")) # title
                new_aired.append(aired)                             # aired
                new_airing.append(airing)                           # airing
                new_watched.append(watched)                         # watched
                new_comment.append(str(row).split(',')[-3][2:-1])   # comment
                new_url.append(str(row).split(',')[-2][2:-1])       # url
                new_season.append(season)                           # season

        ## Combining the data with correct column priorities ##

        if debug == True :print("Combine 01")
        
        for x in range(len(new_info[0])):           # for each title in new
            if debug == True :print("Combine 02")
            if not new_info[0][x] in old_info[0]:   # if the title is not in old_info
                if debug == True :print("Combine 03")
                if debug == True :print(str(new_info[0][x]) +","+ str(new_info[1][x]) +","+ str(new_info[2][x]) +","+ str(new_info[3][x]) +","+ str(new_info[4][x]) +","+ str(new_info[5][x]) +","+ str(new_info[6][x]))
                output_list.append(str(new_info[0][x]) +","+ str(new_info[1][x]) +","+ str(new_info[2][x]) +","+ str(new_info[3][x]) +","+ str(new_info[4][x]) +","+ str(new_info[5][x]) +","+ str(new_info[6][x]))

        if debug == True :
            print("Combine 04")
            print(str(new_info[0][x]))
        for x in range(len(old_info[0])):           # for each title in old
            if debug == True :
                print("Combine 05")
                print(str(old_info[0][x]))

            if not old_info[0][x] in new_info[0]:   # if the title is not in new_info
                if debug == True :print("Combine 06")
                if "-E" in str(old_info[2][x]):
                    if debug == True :print("Combine 07")
                    output_list.append(str(old_info[0][x]) +","+ str(old_info[1][x]) +","+ str(old_info[2][x]) +","+ str(old_info[3][x]) +","+ str(old_info[4][x]) +","+ str(old_info[5][x]) +","+ str(old_info[6][x]))
                else:
                    if debug == True :print("Combine 08")
                    output_list.append(str(old_info[0][x]) +","+ str(old_info[1][x]) +","+ str(old_info[2][x]) +"-E,"+ str(old_info[3][x]) +","+ str(old_info[4][x]) +","+ str(old_info[5][x]) +","+ str(old_info[6][x]))

        for x in range(len(old_info[0])):           # if the titles are in both files
            if debug == True :print("Combine 09")
            if old_info[0][x] in new_info[0]:
                if debug == True :print("Combine 10")
                new_index = new_info[0].index(old_info[0][x])
                old_index = x
                output_list.append(str(new_info[0][new_index]) +","+ str(new_info[1][new_index]) +","+ str(new_info[2][new_index]) +","+ str(old_info[3][old_index]) +","+ str(old_info[4][old_index]) +","+ str(new_info[5][new_index]) +","+ str(old_info[6][old_index]))

#### Saving the data and cleaning up ####
                
        rows = []
        with open('anime_data.csv', 'w', newline='') as file:
            csv_writer = csv.writer(file, delimiter=',')
            output_list.sort(key=lambda x: x.lower())
            for row in output_list:
                rows = row.split(',')
                csv_writer.writerow(rows)

try:
    time.sleep(1) # waiting seems to help actually delete the files
    os.remove('anime_data_old.csv')
    os.remove('anime_data_new.csv')
    shutil.copy('anime_data.csv', 'anime_data.bak')
    print("Extra Files Deleted, Backup created")
except OSError as e:
    pass
