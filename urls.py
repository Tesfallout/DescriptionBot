import csv

title = []      #0
aired = []      #1
airing = []     #2
watched = []    #3
comment = []    #4
url = []        #5

temp = -1

with open('anime_data.csv', 'r', newline='') as csv_file:
    csv_reader = csv.reader(csv_file)

    for row in csv_reader:
        title.append((str(row).split(',')[-7])[2:-1].replace("Ã—","x"))#title
        aired.append(str(row).split(',')[-6][2:-1])     #aired
        airing.append(str(row).split(',')[-5][2:-1])    #airing
        watched.append(str(row).split(',')[-4][2:-1])   #watched
        comment.append(str(row).split(',')[-3][2:-1])   #comment
        url.append(str(row).split(',')[-2][2:-1])       #url

    for x in range(len(title)):
        
        if watched[x] != "D":
            if watched[x].isdigit() and not "-E" in airing[x]:
                print("\n" + title[x] + ": " + comment[x])
                for i in range(int(aired[x])-int(watched[x])):
                    print("<https://aniwave.to" + url[x] + "/ep-" + str(i+1+int(watched[x])) + ">")

            elif "-E" in airing[x]: #show is not on the ongoing page of aniwave anymore
                print("\n" + title[x] + ": " + comment[x])
                temp = int(airing[x].split("-")[0])
                for i in range(temp-int(watched[x])):
                    print("<https://aniwave.to" + url[x] + "/ep-" + str(i+1+int(watched[x])) + ">")
