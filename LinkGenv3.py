import csv
import datetime
import os
import pandas as pd
import re
import requests
import time

from bs4 import BeautifulSoup

def get_anime_season():
    now = datetime.datetime.now()
    month = now.month

    if 1<= month <= 3:
        season = 'winter'
    if 4 <= month <= 6:
        season = 'spring'
    elif 7 <= month <= 9:
        season = 'summer'
    elif 10 <= month <= 12:
        season = 'fall'
    else:
        print("Season Error")

    year = now.year

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

def rename_file(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        #print(f"File '{old_name}' has been renamed to '{new_name}'.")
    except FileNotFoundError:
        pass
        #print(f"File '{old_name}' not found.")
    except PermissionError:
        pass
        #print(f"Permission error. Unable to rename file.")

def get_html_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: Unable to fetch content. Status code: {response.status_code}")
        return None

def extract_show_info(html_content,season,year):
    temp_info_table = []

    soup = BeautifulSoup(html_content, 'html.parser')
    shows = soup.find_all('div', class_='item')

    for show in shows:
        show_info = {}

        # Extracting data-jp attribute from the 'a' tag if it exists

        a_tag = show.select_one('.name.d-title')
        sub_status = show.select_one('.ep-status.sub span')
        total_status = show.select_one('.ep-status.total span')
        a_href = show.select_one('.name.d-title')
        watched_placeholder = 0
        comment_placeholder = ""
        
        if a_tag:
            data_jp = a_tag.get('data-jp', '').strip()
            if data_jp:  # Skip if data-jp is an empty string
                show_info['data-jp'] = data_jp
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

def export_to_csv(data, filename='anime_data_new.csv'):
    # Sort the data by the 'data-jp' key
    sorted_data = sorted(data, key=lambda x: x['data-jp'])

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['data-jp', 'ep-status sub', 'ep-status total', 'watched_placeholder', 'comment_placeholder', 'href', 'season']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write rows without header
        for row in sorted_data:
            writer.writerow(row)

if __name__ == "__main__":
    
    current_season, current_year = get_anime_season()
    last_season, last_season_year = get_last_season(current_season, current_year)
    baseUrl = "https://aniwave.to/filter?keyword=&country%5B%5D=120822&season%5B%5D=" + str(current_season) + "&year%5B%5D=" + str(current_year) + "&type%5B%5D=tv&sort=recently_updated"
    lastUrl = "https://aniwave.to/filter?keyword=&country%5B%5D=120822&season%5B%5D=" + str(last_season) + "&year%5B%5D=" + str(last_season_year) + "&type%5B%5D=tv&sort=recently_updated"

    try:
        os.remove('anime_data_old.csv')
        os.remove('anime_data_new.csv')
    except OSError as e:
        pass
        #print(f"Error deleting file: {e}")

    if not os.path.exists('anime_data.csv'):
        try:
            with open('anime_data.csv', 'w'):
                pass
            #print(f"File anime_data.csv created.")
        except Exception as e:
            pass
            #print(f"Error creating file: {e}")

        
    start_file_name = 'anime_data.csv'
    end_file_name = 'anime_data_old.csv'   
    rename_file(start_file_name, end_file_name)
    
####Get Current Season
    show_info_table = []
    html_content = get_html_content(baseUrl)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')

        page_numbers = re.findall(r'page=\d+', soup.prettify())
        
        show_info_table = extract_show_info(html_content,current_season,current_year)

        # Find how many pages there are
        if page_numbers:
            totalPages = 1
            for page_number in page_numbers:
                pageInt = int(page_number.split('=')[1])
                if pageInt > totalPages:
                    totalPages = pageInt


        pageUrl = baseUrl
        currentPage = 1
        while totalPages > currentPage:
            pageUrl = baseUrl + "&page=" + str(currentPage + 1)
            currentPage += 1
            html_content = get_html_content(pageUrl)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            show_info_table += extract_show_info(html_content,current_season,current_year)

####Get Last Season
            
    html_content = get_html_content(lastUrl)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')

        page_numbers = re.findall(r'page=\d+', soup.prettify())
        
        show_info_table += extract_show_info(html_content,last_season,last_season_year)

        # Find how many pages there are
        if page_numbers:
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
            
            show_info_table += extract_show_info(html_content,last_season,last_season_year)
            

    if show_info_table:
        export_to_csv(show_info_table)




    old_title = [] #0
    old_aired = [] #1
    old_airing = [] #2
    old_watched = [] #3
    old_comment = [] #4
    old_url = [] #5
    old_season = [] #6
    old_info = [old_title,old_aired,old_airing,old_watched,old_comment,old_url,old_season]

    new_title = [] #0
    new_aired = [] #1
    new_airing = [] #2
    new_watched = [] #3
    new_comment = [] #4
    new_url = [] #5
    new_season = [] #6
    new_info = [new_title,new_aired,new_airing,new_watched,new_comment,new_url,new_season]

    output_list = []
    
    with open('anime_data_old.csv', 'r', newline='') as csv_old:
        csv_reader_old = csv.reader(csv_old)

        #header = next(csv_reader_old, None)
        for row in csv_reader_old:
            skip = False
            aired = str(row).split(',')[-6][2:-1]
            airing = str(row).split(',')[-5][2:-1]
            watched = str(row).split(',')[-4][2:-1]
            season = str(row).split(',')[-1][2:-2]

            
            if "N/A" in row:
                skip = True
            if season.split('-')[0] == current_season:
                skip == False
            elif season.split('-')[0] == last_season:
                if aired == airing and watched == "D":
                    skip = True
                elif aired == airing:
                    if watched.isdigit() and not watched > 0:
                        skip = True

            else:
                skip = True


            if skip == False:
                temp = len(str(row).split(',')) #handles extra commas in the show title
                if temp == 7:
                    old_title.append((str(row).split(',')[-7])[2:-1].replace("Ã—","x"))#title
                elif temp == 8:
                    old_title.append((str(row).split(',')[-8] + str(row).split(',')[-7])[2:-1].replace("Ã—","x"))
                elif temp == 9:
                    old_title.append((str(row).split(',')[-9]+ str(row).split(',')[-8] + str(row).split(',')[-7])[2:-1].replace("Ã—","x"))
                old_aired.append(aired)#aired
                old_airing.append(airing)#airing
                old_watched.append(watched)#watched
                old_comment.append(str(row).split(',')[-3][2:-1])#comment
                old_url.append(str(row).split(',')[-2][2:-1])#url
                old_season.append(season)#season

        
        # Open the second CSV file
        with open('anime_data_new.csv', 'r', newline='') as csv_new:
            csv_reader_new = csv.reader(csv_new)

            #header = next(csv_reader_new, None)
            for row in csv_reader_new:
                skip = False
                aired = str(row).split(',')[-6][2:-1]
                airing = str(row).split(',')[-5][2:-1]
                watched = str(row).split(',')[-4][2:-1]
                season = str(row).split(',')[-1][2:-2]


                if "N/A" in row:
                    skip = True
                if season.split('-')[0] == current_season:
                    skip == False
                elif season.split('-')[0] == last_season:
                    if aired == airing:
                        skip = True
                else:
                    skip = True


                if skip == False:  
                    temp = len(str(row).split(',')) #handles extra commas in the show title
                    if temp == 7:
                        new_title.append((str(row).split(',')[-7])[2:-1].replace("Ã—","x"))#title
                    elif temp == 8:
                        new_title.append((str(row).split(',')[-8] + str(row).split(',')[-7])[2:-1].replace("Ã—","x"))
                    elif temp == 9:
                        new_title.append((str(row).split(',')[-9] + str(row).split(',')[-8] + str(row).split(',')[-6])[2:-1].replace("Ã—","x"))
                    new_aired.append(str(row).split(',')[-6][2:-1])#aired
                    new_airing.append(str(row).split(',')[-5][2:-1])#airing
                    new_watched.append(str(row).split(',')[-4][2:-1])#watched
                    new_comment.append(str(row).split(',')[-3][2:-1])#comment
                    new_url.append(str(row).split(',')[-2][2:-1])#url
                    new_season.append(season)#season

            for x in range(len(new_info[0])): #for each title
                if not new_info[0][x] in old_info[0]: #if the title is not in old_info
                    output_list.append(str(new_info[0][x]) +","+ str(new_info[1][x]) +","+ str(new_info[2][x]) +","+ str(new_info[3][x]) +","+ str(new_info[4][x]) +","+ str(new_info[5][x]) +","+ str(new_info[6][x]))

            for x in range(len(old_info[0])): #for each title
                if not old_info[0][x] in new_info[0]: #if the title is not in new_info
                    output_list.append(str(old_info[0][x]) +","+ str(old_info[1][x]) +","+ str(old_info[2][x]) +","+ str(old_info[3][x]) +","+ str(old_info[4][x]) +","+ str(old_info[5][x]) +","+ str(old_info[6][x]))

            for x in range(len(old_info[0])):
                if old_info[0][x] in new_info[0]:
                    new_index = new_info[0].index(old_info[0][x])
                    old_index = x
                    output_list.append(str(new_info[0][new_index]) +","+ str(new_info[1][new_index]) +","+ str(new_info[2][new_index]) +","+ str(old_info[3][old_index]) +","+ str(old_info[4][old_index]) +","+ str(new_info[5][new_index]) +","+ str(old_info[6][old_index]))

            rows = []
            with open('anime_data.csv', 'w', newline='') as file:
                csv_writer = csv.writer(file, delimiter=',')
                output_list.sort(key=lambda x: x.lower())
                for row in output_list:
                    rows = row.split(',')
                    csv_writer.writerow(rows)

    try:
        time.sleep(2)
        os.remove('anime_data_old.csv')
        os.remove('anime_data_new.csv')
        print("Extra Files Deleted")
    except OSError as e:
        pass
                    
            






            
