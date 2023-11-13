import os
import sys
from datetime import datetime, timedelta
import pytz

tz = pytz.timezone("America/Chicago")
now = tz.localize(datetime.now())

# Local Modules
import download
import search

start_year = 2004
year = int(now.strftime("%Y"))
yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
tomorrow = (now - timedelta(days=-1)).strftime("%Y-%m-%d")
week_number = now.strftime("%U")
todays_day = now.strftime("%A")
todays_date = now.strftime("%Y-%m-%d")
todays_date_eu = now.strftime("%d.%m.%Y")

API_KEY = os.getenv("API_KEY", "")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK", "")
VIDEO_DATE = os.getenv("VIDEO_DATE", todays_date_eu)
# Get only current Saturday's video
# PUBLISHED_AFTER = os.getenv("PUBLISHED_AFTER", now.strftime('%Y-%m-%dT00:00:00Z'))
# PUBLISHED_BEFORE =  os.getenv("PUBLISHED_BEFORE", now.strftime(f'{tomorrow}T00:00:00Z'))
# Show is released weekly
EPISODE_NUMBER = os.getenv("EPISODE_NUMBER", int(week_number) - 38)
# Current year + next year - 4031 gives us this season
SEASON_NUMBER = year + (year + 1) - 4031
# YouTube Data API Key
# Zvezde Granda Channel ID
CHANNEL_ID = os.getenv("CHANNEL_ID", "UChz9nfVNmUiZryQtekbzS5g")
# Changes episode number everyweek to match uploaded episode number
QUERY = os.getenv("QUERY", f"Zvezde Granda Cela emisija {todays_date_eu}")
# Save as filename
FILENAME = f"Zvezde Granda - S{SEASON_NUMBER:02}E{EPISODE_NUMBER:02}"
# Max amount of search resultes from YouTube Search API
MAX_RESULTS = 1
# We want MP4 for best playback on Apple devices
FORMAT = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

# Display all passed in variables
# print("***********ENV VARIABLES***********")
# for name, value in os.environ.items():
#     print("{0}: {1}".format(name, value))

# Prevent downloading of the same episode
if os.path.isfile(f"downloads/{FILENAME}"):
    print(f"{FILENAME} already downloaded. Exiting.")
    sys.exit()

# Exit if api key is missing
if not API_KEY:
    print("API_KEY invalid or null")
    sys.exit()

if __name__ == "__main__":
    try:
        search_results = search.channel_videos(QUERY, API_KEY, CHANNEL_ID, MAX_RESULTS)
    except ValueError:
        print("Invalid value!")

    try:
        download.video(search_results, FILENAME, FORMAT, SLACK_WEBHOOK)
        print("downloading")
    except ValueError:
        print("Invalid value!")
