import csv

title = []      #0
aired = []      #1
watched = []    #2
tagline = []    #3
url = []        #4

temp = -1

with open('anime_data.csv', 'r', newline='') as csv_file:
    csv_reader = csv.reader(csv_file)

    for row in csv_reader:
        title.append(str(row).split(',')[0][2:-1])      #title
        aired.append(str(row).split(',')[1][2:-1])      #aired
        watched.append(str(row).split(',')[2][2:-1])    #watched
        tagline.append(str(row).split(',')[3][2:-1])    #tagline
        url.append(str(row).split(',')[4][2:-1])        #url

    for x in range(len(title)):
        if watched[x] != "'D'":
            if watched[x].isdigit() :
                print("\n" + title[x] + ": " + tagline[x])
                for i in range(int(aired[x])-int(watched[x])):
                    print("<https://anitaku.pe/" + url[x] + "-episode-" + str(i+1+int(watched[x])) + ">")
