import csv
import datetime
import os
import shutil
import requests
import time

from bs4 import BeautifulSoup


def responseCode(url):
    # Replace 'http://example.com' with the URL you want to check
    #print(url)

    try:
        response = requests.get(url)
        # Get the status code from the response
        status_code = response.status_code
        #print(f"Response code: {status_code}")
        return status_code
    except requests.RequestException as e:
        # Handle any exceptions that occur during the request
        print(f"An error occurred: {e}")

def get_anime_season():

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

    return season

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

def get_latest_ep(hrefs, titles, latestEp) :
    
    for x in range(len(hrefs)) :
        code = 200
        ep = 1
        dropped = False

        with open('anime_data_old.csv', 'r', encoding='utf-8') as file: #MUST BE INSIDE ABOVE FOR LOOP
            data_old = csv.reader(file)

            for row in data_old :
                if titles[x] == row[0] :
                    if row[2] == "D" or row[1] == "D":
                        dropped = True
                        ep = "D"
                        code = 404
                        break
                    else :
                        ep = int(row[1])
                            
            while code != 404 :
                url = "https://anitaku.pe/" + str(hrefs[x]) + "-episode-"+str(ep)
                code = responseCode(url)
                if code != 404 :
                    ep += 1
                elif ep > 1 :
                    ep -= 1
                else :
                    ep = 1
                    url = "https://anitaku.pe/" + str(hrefs[x]) + "-episode-"+str(ep)
                    code = responseCode(url)
                    if code == 404 :
                        ep = 0
            
        #if not dropped :
            #print(str(titles[x]) + " : " + str(ep))
        latestEp.append(ep)
    

def seasonUrl(season, year):
    url = 'https://anitaku.pe/sub-category/' + str(season) + "-" + str(year) + "-anime"
    return url

def scrapeSeason(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        page_links = soup.select("ul.pagination-list li a")
        page_numbers = [int(link['data-page']) for link in page_links]
        max_page = max(page_numbers)
        #print("max page: " + str(max_page))

    except requests.RequestException as e:
        print(f"An error occurred while getting number of pages: {e}")

        
    try:
        hrefs = []
        titles = []
        page = 1
        while page <= max_page:
            page_url = str(url) + "?page=" + str(page)
            print(page_url)
            
            response = requests.get(page_url)
            soup = BeautifulSoup(response.text, 'html.parser')
           
            last_episodes_divs = soup.find_all('div', class_='last_episodes') # Find all <div> elements with class 'last_episodes'
            
            for div in last_episodes_divs:
                p_tags = div.find_all('p', class_='name') # Find all <p> tags with class 'name' within this <div>
                
                for p in p_tags:
                    a_tags = p.find_all('a') # Find all <a> tags within this <p>
                    for a in a_tags:
                        href = a.get('href')
                        if href:
                            if href.split("-")[-1] != "dub" and href.split("-")[-1] != "uncensored" :
                                href = href.split("/")[2]
                                #print(href)
                                hrefs.append(href)

                        title = a.get('title') # Extract the title attribute from the <a> tag
                        if title:
                            if "(Dub)" not in title and "(Uncensored)" not in title:
                                title = title.replace(",","")#remove commas from titles
                                title = title.replace("\"","")
                                title = title.replace("é","e")
                                title = title.replace("Ã—","x")
                                title = title.replace("♡","")
                                title = title.replace("â™¡","")
                                #print(title)
                                titles.append(title)

            page += 1

        #print(hrefs)
        #print(titles)
        return hrefs, titles
    
    except requests.RequestException as e:
        print(f"An error occurred while pulling show urls: {e}")

### Database Checking and Handling

# Check Status of Files
fileStatus = 1000
if os.path.exists('anime_data.csv'):
    fileStatus += 100

if os.path.exists('anime_data_old.csv'):
    fileStatus += 10

if os.path.exists('anime_data.bak'):
    fileStatus += 1

print(fileStatus)

### Handle File Statuses

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

#Prep some variables
now = datetime.datetime.now()
month = now.month
year = now.year

season = get_anime_season()
url = seasonUrl(season, year)
#print(url)
responseCode(url)

last_season, last_season_year = get_last_season(season, year)
last_season_url = seasonUrl(last_season, last_season_year)
#print(last_season_url)
responseCode(last_season_url)

###Rename anime_data.csv to anime_data_old.csv
shutil.move('anime_data.csv','anime_data_old.csv')

##############################################


###Generate anime_data_new.csv
#Check to make sure lists are equal length
Continue = True

hrefs, titles = scrapeSeason(url)
last_season_hrefs, last_season_titles = scrapeSeason(last_season_url)

entryType = []
last_season_entryType = []

for x in range(len(hrefs)) :
    entryType.append("Auto")
for x in range(len(last_season_hrefs)) :
    last_season_entryType.append("Auto")
    

with open('anime_data_old.csv', 'r', encoding='utf-8') as file:
            data_old = csv.reader(file)
            for row in data_old :
                if row[6] == "Manual":
                    if  row[5] == (str(season)+"-"+str(year)) :
                        titles.append(row[0])
                        hrefs.append(row[4])
                        entryType.append("Manual")

                    elif row[5] == (str(last_season)+"-"+str(last_season_year)) :
                        last_season_titles.append(row[0])
                        last_season_hrefs.append(row[4])
                        last_season_entryType.append("Manual")

                    print(str(row[0]) + " Added Manually")

if len(hrefs) != len(titles) :
    print("ERROR : hrefs and titles are NOT same length")
    Continue = False
if len(last_season_hrefs) != len(last_season_titles) :
    print("ERROR : last_season_hrefs and last_season_titles are NOT same length")
    Continue = False


## Gen latestEp[]
    
if Continue :
    latestEp = []
    last_season_latestEp = []
    
    get_latest_ep(hrefs, titles, latestEp)
    get_latest_ep(last_season_hrefs, last_season_titles, last_season_latestEp)


    if len(latestEp) != len(hrefs) :
        print("ERROR : latestEp and hrefs are NOT same length")
        Continue = False

    if len(last_season_latestEp) != len(last_season_hrefs) :
        print("ERROR : last_season_latestEp and last_season_hrefs are NOT same length")
        Continue = False
        
# 0 : Title
# 1 : Latest Ep Released
# 2 : Last Ep Watched / D
# 3 : Tagline
# 4 : url
# 5 : season in format: summer-2024
# 6 : added Manual or Auto

    #get last eps and taglines

    watchedEp = []
    last_season_watchedEp = []

    tagline = []
    last_season_tagline = []

    for title in titles:
        titleMissing = True
        with open('anime_data_old.csv', 'r', encoding='utf-8') as file:
            data_old = csv.reader(file)
            for row in data_old :
                if title == row[0]:
                    watchedEp.append(row[2])
                    tagline.append(row[3].replace(",",""))
                    titleMissing = False
                    break
            if titleMissing :
                print("Title not found in _old:" + str(title))
                watchedEp.append("0")
                tagline.append("Title not found in _old")

    for title in last_season_titles:
        titleMissing = True
        with open('anime_data_old.csv', 'r', encoding='utf-8') as file:
            data_old = csv.reader(file)
            for row in data_old :
                if title == row[0]:
                    last_season_watchedEp.append(row[2])
                    last_season_tagline.append(row[3].replace(",",""))
                    titleMissing = False
                    break
            if titleMissing :
                print("Problem Show:" + str(title))
                last_season_watchedEp.append("0")
                last_season_tagline.append("Problem with Show Title")



    #generate output_list
    output_list = []

    #print("titles: " + str(len(titles)))
    #print("hrefs: " + str(len(hrefs)))
    #print("entryType: " + str(len(entryType)))
    #print("latestEp: " + str(len(latestEp)))
    #print("watchedEp: " + str(len(watchedEp)))
    #print("tagline: " + str(len(tagline)))
    #print("last_season_titles: " + str(len(last_season_titles)))
    #print("last_season_hrefs: " + str(len(last_season_hrefs)))
    #print("last_season_entryType: " + str(len(last_season_entryType)))
    #print("last_season_latestEp: " + str(len(last_season_latestEp)))
    #print("last_season_watchedEp: " + str(len(last_season_watchedEp)))
    #print("last_season_tagline: " + str(len(last_season_tagline)))

    #for x in len
    #print(titles)
    #print(tagline)

    
    
    for x in range(len(titles)) :
        output_list.append(str(titles[x]) + "," + str(latestEp[x]) + "," + str(watchedEp[x]) + "," + str(tagline[x]) + "," + str(hrefs[x]) + "," + str(season)+"-"+str(year) + "," + entryType[x])
        
    for x in range(len(last_season_titles)) :
        output_list.append(str(last_season_titles[x]) + "," + str(last_season_latestEp[x]) + "," + str(last_season_watchedEp[x]) + "," + str(last_season_tagline[x]) + "," + str(last_season_hrefs[x]) + "," + str(last_season)+"-"+str(last_season_year) + "," + last_season_entryType[x])
        
    with open('anime_data.csv', 'w', newline='',encoding='utf-8') as file:
        csv_writer = csv.writer(file, delimiter=',')
        output_list.sort(key=lambda x: x.lower())
        for row in output_list:
            rows = row.split(',')
            csv_writer.writerow(rows)

    os.remove('anime_data_old.csv')
        
##############################################



