import requests
import os
import configparser
from concurrent.futures import ThreadPoolExecutor

# Reading config
config = configparser.ConfigParser()
config.read("config.ini")

site = config.get("AniBatch", "site")
path = config.get("AniBatch", "path")
API = config.get("AniBatch", "API")
amount = config.get("AniBatch", "amount")

# Searching
IN = input("What's the name of the anime | ")
IN = IN.replace(" ", "-").replace("/", "-")  # Replace spaces and slashes with hyphens
url = f"{API}/anime/{site}/{IN}"

response = requests.get(url)
animelist = response.json()

results = animelist.get("results", [])

for i, result in enumerate(results, start=1):
    anime_id = result.get("id", "")
    title = result.get("title", "")
    print(f"{i}: Title: {title}")

N = input("Select the number | ")

try:
    selected_number = int(N)
    if 1 <= selected_number <= len(results):
        selected_anime = results[selected_number - 1]
        selected_id = selected_anime.get("id", "")
    else:
        print("Invalid selection.")
except ValueError:
    print("Invalid input. Please enter a valid number.")

# Fetching Show Information
print("Fetching info...")
if site == "gogoanime":
    url = f"{API}/anime/{site}/info/" + selected_id
    response = requests.get(url)
    data = response.json()
else:
    url = f"{API}/anime/zoro/info?id={selected_id}"
    response = requests.get(url)
    data = response.json()
    id = data.get("number", [])
    print(id)

# Check if there are episodes in the data
episodes = data.get("episodes", [])

if response.status_code == 200 and episodes:
    # Find the highest episode number
    highest_episode = max(episodes, key=lambda x: x["number"])
    print("Highest Episode:", highest_episode["number"])

    # Fetching Links and Downloading Episodes
    if site == "gogoanime":
        linksurl_base = f"{API}/anime/{site}/watch/{selected_id}-episode-"
    else:
        linksurl_base = f"{API}/anime/{site}/watch/"

    # Set a default quality (e.g., '720p')
    print("Select a quality | ")
    print("1: 1080p")
    print("2: 720p")
    print("3: 480p")
    print("4: 360p")

    quality_options = {
        1: "1080p",
        2: "720p",
        3: "480p",
        4: "360p"
    }

    N = input("Select the number | ")

    # Make sure the input is a valid key in the dictionary
    try:
        selected_quality = quality_options[int(N)]
        print(f"Selected quality: {selected_quality}")
        default_quality = selected_quality
    except (ValueError, KeyError):
        print("Invalid selection. Please enter a valid number.")

    # Define the download_episode function here
    def download_episode(linksurl, Download_ID, episode_number, selected_id, default_quality, path):
        print(f"Downloading Episode {episode_number} with the default quality ({default_quality})...")

        output_filename = f'"{selected_id} E{episode_number:02}".mp4'
        ffmpeg_command = f'ffmpeg -i "{Download_ID}" -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 {output_filename}'

        os.system("ffmpeg -i " + Download_ID + " -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 " + os.path.join(path, output_filename))

    # Download the episodes using the selected quality
    with ThreadPoolExecutor(max_workers=int(amount)) as executor:
        futures = []

        for episode_number in range(1, highest_episode["number"] + 1):
            linksurl = f"{linksurl_base}{episode_number}"
            print(f"Submitting download task for Episode {episode_number}...")

            response = requests.get(linksurl)
            links_data = response.json()
            sources = links_data.get('sources', [])

            # Check if default quality is available
            if any(source.get('quality', '').lower() == default_quality.lower() for source in sources):
                selected_quality = next(source for source in sources if source.get('quality', '').lower() == default_quality.lower())
                Download_ID = '"{}"'.format(selected_quality.get("url", ""))

                # Submit the download task to the ThreadPoolExecutor
                future = executor.submit(download_episode, linksurl, Download_ID, episode_number, selected_id, default_quality, path)
                futures.append(future)
            else:
                print(f"Default quality ({default_quality}) not available for Episode {episode_number}. Skipping.")

        # Wait for all download tasks to complete
        for future in futures:
            future.result()

    print("All episodes downloaded successfully.")
else:
    print("Failed to retrieve data or no episodes found. Status code:", response.status_code)
