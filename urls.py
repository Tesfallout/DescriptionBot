import csv

url = []        #0
title = []      #1
watched = []    #2
tagline = []    #3


temp = -1

with open('anime_data.csv', 'r', newline='') as csv_file:
    csv_reader = csv.reader(csv_file)

    for row in csv_reader:
        url.append(row[0].strip())       # URL
        title.append(row[1].strip())     # Title
        watched.append(row[2].strip())   # Watched
        tagline.append(row[3].strip())   # Tagline
        

    for x in range(len(title)):
        if watched[x] != "D":
            if watched[x].isdigit() :
                print("\n" + title[x] + ": " + tagline[x] + "\nLast Watched: " + watched[x] + "\n<https://hianime.to/watch/" + url[x] + ">")
