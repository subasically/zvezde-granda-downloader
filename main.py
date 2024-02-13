import os
import sys
import schedule
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config import Configuration

config = Configuration('config.json')

load_dotenv()

# Local Modules
import download
import search
from pytz import timezone
import time

debug = os.getenv("DEBUG", "False")

def print_debug(*args, **kwargs):
    if debug == "True":
        print(*args, **kwargs)


API_KEY = os.getenv("API_KEY", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
SLACK_WEBHOOK = os.getenv(
    "SLACK_WEBHOOK",
    "",
)

FORMAT = os.getenv("FORMAT", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
SCHEDULE = os.getenv("SCHEDULE", "0 16-23 * * 6") # Saturday from 4 PM to 11 PM

print_debug(f"**************************************************")
print_debug(f"***************** DEBUGGING: {debug} ****************")
print_debug(f"**************************************************")

timezones = os.getenv("TIMEZONE", "US/Central")
tz = timezone(timezones)
now = datetime.now(tz)

print_debug(f"Current Time ({timezones}):", now.strftime("%Y-%m-%d %H:%M:%S"))

episode_adjustment = int(os.getenv("EPISODE_ADJUSTMENT", 1))
start_date = os.getenv("START_DATE", now.strftime("2023-09-23"))
start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
start_date_year = datetime.strptime(start_date, "%Y-%m-%d").year
today = now.strftime("%Y-%m-%d")
yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")  # -1 day
tomorrow = (now - timedelta(days=-1)).strftime("%Y-%m-%d")  # +1 day
week_number = now.strftime("%U")  # 01-53
todays_day = now.strftime("%A")
todays_date = now.strftime("%Y-%m-%d")

if todays_day == "Saturday":
    print_debug("Saturday")
    video_date = now.strftime("%d.%m.%Y")  # 31.12.2022
elif todays_day == "Sunday":
    print_debug("Sunday")
    video_date = (now - timedelta(days=1)).strftime("%d.%m.%Y")  # 02.01.2023
elif todays_day == "Monday":
    print_debug("Monday")
    video_date = (now - timedelta(days=2)).strftime("%d.%m.%Y")
elif todays_day == "Tuesday":
    print_debug("Tuesday")
    video_date = (now - timedelta(days=3)).strftime("%d.%m.%Y")
elif todays_day == "Wednesday":
    print_debug("Wednesday")
    video_date = (now - timedelta(days=4)).strftime("%d.%m.%Y")
elif todays_day == "Thursday":
    print_debug("Thursday")
    video_date = (now - timedelta(days=5)).strftime("%d.%m.%Y")
elif todays_day == "Friday":
    print_debug("Friday")
    video_date = (now - timedelta(days=6)).strftime("%d.%m.%Y")
else:
    video_date = now.strftime("%d.%m.%Y")

VIDEO_DATE = os.getenv("VIDEO_DATE", video_date)
SEASON_NUMBER = os.getenv("SEASON_NUMBER", start_date_year - 2008)

now = now.replace(tzinfo=None)  # Convert to naive datetime object
weeks_since_start = (now - start_date_obj).days // 7  # 0-52
EPISODE_NUMBER = os.getenv("EPISODE_NUMBER", weeks_since_start + episode_adjustment)

QUERY = os.getenv(
    "QUERY", f"Zvezde Granda - Cela emisija {EPISODE_NUMBER:02} - {VIDEO_DATE}"
)
FILENAME = f"Zvezde Granda - S{SEASON_NUMBER:02}E{EPISODE_NUMBER:02} - {VIDEO_DATE}"
MAX_RESULTS = 1

# print_debug(FILENAME)

# Prevent downloading of the same episode
if os.path.isfile(f"downloads/{FILENAME}"):
    print(f"{FILENAME} already downloaded. Exiting.")
    sys.exit()

# Exit if api key is missing
if not API_KEY:
    print("⚠️ API_KEY invalid or null ⚠️")
    sys.exit()

if not CHANNEL_ID:
    print("⚠️ CHANNEL_ID invalid or null ⚠️")
    sys.exit()
    
def episode_file_exists():
    try:
        # Check if season,episode exists in downloads_history.csv
        if os.path.isfile("downloads/downloads_history.csv"):
            with open("downloads/downloads_history.csv", "r") as f:
                lines = f.readlines()
                for line in lines:
                    print_debug(f"downloads_history.csv: {line}")
                    print_debug(f"SEASON_NUMBER,{SEASON_NUMBER}")
                    if f"{SEASON_NUMBER},{EPISODE_NUMBER}" in line:
                        print_debug(f"{FILENAME} already downloaded. Exiting.")
                        
                        # Quit program if episode already downloaded
                        sys.exit()
    except ValueError:
        print_debug("⚠️ Invalid downloads_history.csv value!")
        sys.exit()

def run_downloader():
    if episode_file_exists():
        # print_debug(f"{FILENAME} already downloaded. Exiting.")
        sys.exit()
        
    try:
        search_results = search.channel_videos(QUERY, API_KEY, CHANNEL_ID, MAX_RESULTS)
    except ValueError:
        print("⚠️ Invalid search value!")

    try:
        # verify that episode number in FILENAME matches the search_results episode number
        print_debug(
            f"Verify that episode number in FILENAME matches the search_results episode number."
        )
        try:
            search_results_episode_number = FILENAME.split("-")[1].split("E")[1].strip()
        except IndexError:
            print_debug("⚠️ Invalid episode number!")
            sys.exit()
        # print(f"EPISODE_NUMBER: {EPISODE_NUMBER}")
        # print(f"search_results_episode_number: {search_results_episode_number}")

        if int(EPISODE_NUMBER) != int(search_results_episode_number):
            print_debug("⚠️ Episode numbers do not match!")
            raise ValueError
        else:
            print_debug("✅ Episode numbers match! Proceeding with download.")
    except ValueError:
        print_debug("Invalid episode number!")
        sys.exit()

    try:
        download.video(search_results, FILENAME, FORMAT, SLACK_WEBHOOK, SEASON_NUMBER, EPISODE_NUMBER, todays_date)
    except ValueError:
        print_debug("⚠️ Invalid download value!")

if __name__ == "__main__":
    schedule.every().cron(SCHEDULE).do(run_downloader)

    while True:
        schedule.run_pending()
        time.sleep(1)
