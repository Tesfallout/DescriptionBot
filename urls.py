import csv

title = [] #0
aired = [] #1
watched = [] #3
comment = [] #4
url = [] #5

with open('anime_data.csv', 'r', newline='') as csv_file:
    csv_reader = csv.reader(csv_file)

    for row in csv_reader:
        title.append((str(row).split(',')[-7])[2:-1].replace("Ã—","x"))#title
        aired.append(str(row).split(',')[-6][2:-1])     #aired
        watched.append(str(row).split(',')[-4][2:-1])   #watched
        comment.append(str(row).split(',')[-3][2:-1])   #comment
        url.append(str(row).split(',')[-2][2:-1])       #url

    for x in range(len(title)):
        if watched[x] != "D" and watched[x].isdigit():
            print("\n" + title[x] + ": " + comment[x])
            for i in range(int(aired[x])-int(watched[x])):
                print("<https://aniwave.to" + url[x] + "/ep-" + str(i+1+int(watched[x])) + ">")
            

    
