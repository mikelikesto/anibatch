import requests
import os
# Searching
IN = input("What's the name of the anime | ")
IN = IN.replace(" ", "-").replace("/", "-")  # Replace spaces and slashes with hyphens
url = f"https://api.consumet.org/anime/gogoanime/{IN}"

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
url = "https://api.consumet.org/anime/gogoanime/info/" + selected_id
response = requests.get(url)
data = response.json()

if response.status_code == 200:
    episodes = data.get("episodes", [])

    # Check if there are episodes in the data
    if episodes:
        # Find the highest episode number
        highest_episode = max(episodes, key=lambda x: x["number"])

        # Print the highest episode number
        print("Highest Episode:", highest_episode["number"])

        # Fetching Links and Downloading Episodes
        linksurl_base = f"https://api.consumet.org/anime/gogoanime/watch/{selected_id}-episode-"

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

        try:
            selected_number = int(N)
            if 1 <= selected_number <= len(results):
                selected_anime = results[selected_number - 1]
                selected_id = selected_anime.get("id", "")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

        # Download the episodes using the selected quality
        for episode_number in range(1, highest_episode["number"] + 1):
            linksurl = f"{linksurl_base}{episode_number}"
            print(f"Downloading Episode {episode_number} with the default quality ({default_quality})...")

            response = requests.get(linksurl)
            links_data = response.json()
            sources = links_data.get('sources', [])

            # Check if default quality is available
            if any(source.get('quality', '').lower() == default_quality.lower() for source in sources):
                selected_quality = next(source for source in sources if source.get('quality', '').lower() == default_quality.lower())
                Download_ID = '"{}"'.format(selected_quality.get("url", ""))
                print(f"Selected Quality ID for Episode {episode_number}: {Download_ID}")

                # Download the episode using the selected quality
                output_filename = f"{selected_id} E{episode_number}.mp4"
                print(linksurl)
                print(Download_ID)
                #Eposide naming for jellyfin and plexser
                episode_number_str = str(episode_number).zfill(2)

                output_filename = f'"{selected_id} E{episode_number_str}".mp4'
                ffmpeg_command = f'ffmpeg -i "{Download_ID}" -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 {output_filename}'



                os.system("ffmpeg -i " + Download_ID + " -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 " + output_filename)

            else:
                print(f"Default quality ({default_quality}) not available for Episode {episode_number_str}. Skipping.")

    else:
        print("No episodes found.")
else:
    print("Failed to retrieve data. Status code:", response.status_code)