import csv
import requests
from bs4 import BeautifulSoup

def get_ongoing_show_titles(url):
    show_titles = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title_elements = soup.select('div[data-tip="ongoing"] a')
        show_titles = [title.text for title in title_elements]
    else:
        print("Error accessing the ongoing shows page.")
    return show_titles


def get_last_episode_watched(anime_url):
    response = requests.get(anime_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        episode_status = soup.select_one('.ep-status')
        if episode_status:
            return int(episode_status.text.strip())
    return 0


def generate_episode_links(url, next_episode, last_watched_episode):
    base_url = f'{url}/ep-'
    episode_links = []

    for episode in range(int(last_watched_episode) + 1, int(next_episode) + 1):
        episode_links.append(f"<https://9anime.to/watch/{base_url}{episode}>")

    return episode_links


def get_all_show_titles(url):
    show_titles = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title_elements = soup.select('.item .inner .ani a')
        show_titles = [title['href'].split('/')[-1] for title in title_elements]
    else:
        print("Error accessing the shows page.")
   
    return show_titles



def prepare_for_url(string):
    # Remove special characters, keep only alphanumeric characters and spaces
    string = ''.join(char if char.isalnum() or char.isspace() else '' for char in string)

    # Convert to lowercase
    string = string.lower()

    # Replace spaces with hyphens
    string = string.replace(' ', '-')

    return string

def find_url(search_string, array):

    for i in range(len(search_string), 0, -1):
        current_search = search_string[:i]
        for element in array:
            if current_search in element:
                return element
    return None, None

def main():
    #ongoing_url = "https://9anime.to/ongoing"
    ongoing_url = "https://9anime.to/filter?keyword=&country%5B%5D=120822&season%5B%5D=summer&year%5B%5D=2023&type%5B%5D=tv&status%5B%5D=releasing&language%5B%5D=sub&sort=recently_updated"
    ongoing_show_titles = get_all_show_titles(ongoing_url)
    if not ongoing_show_titles:
        print("No ongoing show titles found.")
        return

    with open("SeasonStatus.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file)

        for row in csv_reader:
            title, next_airing_episode, last_episode_watched, comment = row

            # Skip rows with 'N' or 'D' in next_airing_episode or last_episode_watched
            if last_episode_watched.isdigit():

                if not next_airing_episode.isdigit():
                    next_airing_episode = int(last_episode_watched)+1

                next_airing_episode = int(next_airing_episode)
                last_episode_watched = int(last_episode_watched)
                urlTitle = prepare_for_url(title)
                anime_url = find_url(urlTitle,ongoing_show_titles)

                episode_links = generate_episode_links(anime_url, int(next_airing_episode)-1, last_episode_watched)
                if episode_links:
                    print(f"\n{title}: "+ comment)
                    for url in episode_links:
                        print(url)
            

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("An error occurred while running the script:")
        print(e)
