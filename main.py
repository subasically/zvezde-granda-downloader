import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# import pytz

# Local Modules
import download
import search
from pytz import timezone

debug = os.getenv("DEBUG", "False")


def print_debug(*args, **kwargs):
    if debug == "True":
        print(*args, **kwargs)


API_KEY = os.getenv("API_KEY", "")
SLACK_WEBHOOK = os.getenv(
    "SLACK_WEBHOOK",
    "",
)
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

print_debug(f"**************************************************")
print_debug(f"***************** DEBUGGING: {debug} ****************")
print_debug(f"**************************************************")

timezones = os.getenv("TIMEZONE", "US/Central")
tz = timezone(timezones)
now = datetime.now(tz)

print_debug(f"Current Time ({timezones}):", now.strftime("%Y-%m-%d %H:%M:%S"))

episode_adjustment = int(os.getenv("EPISODE_ADJUSTMENT", 1))
start_date = os.getenv("START_DATE", now.strftime("2023-09-23"))  # 2023-09-23
start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")  # 2023-09-23
start_date_year = datetime.strptime(start_date, "%Y-%m-%d").year  # 2023
today = now.strftime("%Y-%m-%d")  # 2023-01-01
yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")  # -1 day
tomorrow = (now - timedelta(days=-1)).strftime("%Y-%m-%d")  # +1 day
week_number = now.strftime("%U")  # 01-53
todays_day = now.strftime("%A")  # Monday
todays_date = now.strftime("%Y-%m-%d")  # 2023-01-01

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
FORMAT = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

# print(FILENAME)

# Prevent downloading of the same episode
if os.path.isfile(f"downloads/{FILENAME}"):
    print_debug(f"{FILENAME} already downloaded. Exiting.")
    sys.exit()

# Exit if api key is missing
if not API_KEY:
    print("⚠️ API_KEY invalid or null")
    sys.exit()

if not CHANNEL_ID:
    print("⚠️ CHANNEL_ID invalid or null")
    sys.exit()

if __name__ == "__main__":
    try:
        search_results = search.channel_videos(QUERY, API_KEY, CHANNEL_ID, MAX_RESULTS)
    except ValueError:
        print("⚠️ Invalid search value!")

    try:
        # verify that episode number in FILENAME matches the search_results episode number
        print(
            f"Verify that episode number in FILENAME matches the search_results episode number."
        )
        try:
            search_results_episode_number = FILENAME.split("-")[1].split("E")[1].strip()
        except IndexError:
            print("⚠️ Invalid episode number!")
            sys.exit()
        print_debug(f"EPISODE_NUMBER: {EPISODE_NUMBER}")
        print_debug(f"search_results_episode_number: {search_results_episode_number}")

        if int(EPISODE_NUMBER) != int(search_results_episode_number):
            print("⚠️ Episode numbers do not match!")
            raise ValueError
        else:
            print("✅ Episode numbers match! Proceeding with download.")
    except ValueError:
        print("Invalid episode number!")
        sys.exit()

    try:
        download.video(search_results, FILENAME, FORMAT, SLACK_WEBHOOK)
    except ValueError:
        print("⚠️ Invalid download value!")
