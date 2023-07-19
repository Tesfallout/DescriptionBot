import re
import time
import os
import csv
from selenium import webdriver
from bs4 import BeautifulSoup

def get_next_episode(episode_text):
    if "aired" in episode_text:
        return int(episode_text.split(" ")[1]) + 1
    elif "airing" in episode_text:
        return int(episode_text.split(" ")[1])
    else:
        return None

def should_exclude_show(title, episode_number):
    # List of words that indicate a show should be excluded
    exclude_keywords = [
        "aiyou", "bai", "biaoren", "bing", "ch", "cheng", "da", "dalu", "diyi", "du", "feng", "ge", 
        "he", "huo", "ji", "jiyuan", "jing", "jiyuan", "jue", "lan", "lian", "nüshen", "quanzhi", "qing",
        "sh", "shen", "sheng", "shiguang", "shijie", "shuo", "ta", "tian", "wu", "wushen", "xiao", "xiaolan", "xuan", "xulie", "xyrin",
        "yan", "yaun", "ye", "ye", "yishi", "yuan", "yuan", "zhan", "zhe", "zen", "zh", "zhun", "zhan", "zhe",
        "zhun", "zhi", "zhu", "zhuan", "zhuzai", "zhi"
    ]

    title = title.lower()

    # Check if any word in the title matches the exclude keywords
    for keyword in exclude_keywords:
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, title):
            return True

    # Check if the episode number is greater than 60
    if episode_number is not None and episode_number > 60:
        return True

    return False

def scrape_anichart():
    url = "https://anichart.net/airing"

    # Set up Firefox webdriver with geckodriver.exe and specify Firefox binary path
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Run the browser in headless mode (no GUI)
    options.binary_location = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
    driver = webdriver.Firefox(options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Wait for the page to load (adjust this if needed)

        # Get the page source after waiting
        page_source = driver.page_source
        driver.quit()  # Close the browser

        soup = BeautifulSoup(page_source, "html.parser")
        anime_list = soup.select(".airing-card")

        anime_titles = []
        ep_number = []

        for anime in anime_list:
            title = anime.select_one(".title").text.strip()
            episode_info = anime.select_one(".airing").text.strip()
            next_episode = get_next_episode(episode_info)

            # Update the anime_titles and ep_number lists
            if next_episode is not None and not should_exclude_show(title, next_episode):
                anime_titles.append(title)
                ep_number.append(next_episode)

        return anime_titles, ep_number  # Return the lists

    except Exception as e:
        print(f"An error occurred: {e}")
        driver.quit()
        return None, None

if __name__ == "__main__":
    anime_titles, ep_number = scrape_anichart()

    try:
        if anime_titles is not None and ep_number is not None:
            anime_data = {}
            status = "0"
            comment = "0"

            # Store anime titles and their corresponding episode numbers in a dictionary
            for title, episode in zip(anime_titles, ep_number):

                if os.path.exists("SeasonStatus.csv"):
                    with open('SeasonStatus.csv', 'r', newline="") as csvfile:
                        reader = csv.reader(csvfile)
                        for row in reader:
                            if row[0] == title:
                                status = row[2]
                                comment = row[3]
                                break

                anime_data[title] = episode, status, comment

            myKeys = list(anime_data.keys())
            myKeys.sort()
            anime_data_sorted = {i: anime_data[i] for i in myKeys}

            output = []
            for i in myKeys:
                output.append([i, anime_data[i][0], anime_data[i][1], anime_data[i][2]])
                              

            with open('SeasonStatus.csv', 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows(output)

            print("Data written to SeasonStatus.csv.")
        else:
            print("Error occurred while scraping. Please check the URL and try again.")

    except Exception as e:
        print("An error occurred while running the script:")
        print(e)
