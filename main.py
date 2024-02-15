import os
import time
import sys
import schedule
import requests
import yt_dlp
import notification
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pytz import timezone
import math

load_dotenv()

API_KEY = os.getenv("API_KEY", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK", "")
FORMAT = os.getenv("FORMAT", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
SCHEDULE = os.getenv("SCHEDULE", "@30min")
timezones = os.getenv("TIMEZONE", "US/Central")

tz = timezone(timezones)
now = datetime.now(tz)

def get_timestamp():
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


# Possible Options: @5min, @15min, @30min, @hourly, @daily, @weekly

debug = os.getenv("DEBUG", "False")

def print_debug(*args, **kwargs):
    if debug == "True":
        tstamp = get_timestamp()
        print(f"[{tstamp}]", *args, **kwargs)

if debug == "True":
    print(f"**************************************************")
    print(f"***************** DEBUGGING: {debug} ****************")
    print(f"**************************************************")

print(f"\nContainer Timezone: ({timezones})")
print(f"\nContainer Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")

episode_adjustment = int(os.getenv("EPISODE_ADJUSTMENT", 1))
start_date = os.getenv("START_DATE", now.strftime("2023-09-23"))
start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
start_date_year = start_date_obj.year
today = now.strftime("%Y-%m-%d")
yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")  # -1 day
tomorrow = (now - timedelta(days=-1)).strftime("%Y-%m-%d")  # +1 day
week_number = now.strftime("%U")  # 01-53
todays_day = now.strftime("%A")
todays_date = now.strftime("%Y-%m-%d")

day_to_date = {
    "Saturday": now.strftime("%d.%m.%Y"),
    "Sunday": (now - timedelta(days=1)).strftime("%d.%m.%Y"),
    "Monday": (now - timedelta(days=2)).strftime("%d.%m.%Y"),
    "Tuesday": (now - timedelta(days=3)).strftime("%d.%m.%Y"),
    "Wednesday": (now - timedelta(days=4)).strftime("%d.%m.%Y"),
    "Thursday": (now - timedelta(days=5)).strftime("%d.%m.%Y"),
    "Friday": (now - timedelta(days=6)).strftime("%d.%m.%Y"),
}

video_date = day_to_date.get(todays_day, now.strftime("%d.%m.%Y"))

VIDEO_DATE = os.getenv("VIDEO_DATE", video_date)
SEASON_NUMBER = os.getenv("SEASON_NUMBER", str(start_date_year - 2008))

now = now.replace(tzinfo=None)  # Convert to naive datetime object
weeks_since_start = (now - start_date_obj).days // 7  # 0-52
EPISODE_NUMBER = os.getenv("EPISODE_NUMBER", str(weeks_since_start + episode_adjustment))

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

def save_thumbnail(url, filename):
    print_debug(f"[Save_Thumbnail] Saving thumbnail {filename}...")
    data = requests.get(url).content
    f = open(f"downloads/{filename}", "wb")
    f.write(data)
    f.close()

def download(response):
    ydl_options = {
        "outtmpl": "downloads/" + FILENAME,
        "format": FORMAT,
        "quiet": os.getenv("YDL_QUIET", "True"),
        "no_warnings": os.getenv("YDL_NO_WARNINGS", "True"),
    }
    ydl = yt_dlp.YoutubeDL(ydl_options)

    for item in response["items"]:
        video_url = "http://www.youtube.com/watch?v=" + item["id"]["videoId"]
        thumbnail_url = item["snippet"]["thumbnails"]["high"]["url"]
        thumb_max_url = thumbnail_url.replace("hqdefault", "maxresdefault")

        print_debug("[Download] Downloading thumbnail", f"{FILENAME}.png")
        save_thumbnail(thumb_max_url, f"{FILENAME}.png")

        try:
            print_debug("[Download] Downloading", FILENAME)
            ydl.download([video_url])

        except Exception as e:
            print_debug("[Download] ⚠️ Error downloading video!")
            print(e)
            sys.exit()

        if SLACK_WEBHOOK:
            print_debug("[Download] Sending notification to Slack")
            notification.slack(
                SLACK_WEBHOOK, "New Episode! ✌️", FILENAME, thumb_max_url
            )
        else:
            print_debug("[Download] ☹️ No Slack webhook provided. Notification will not be sent. Exiting.")
            sys.exit()

def search():
    print_debug("[Search] Searching for new episodes...", QUERY)
    youtube = build("youtube", "v3", developerKey=API_KEY)

    request = youtube.search().list(
        part="snippet",
        q=QUERY,
        maxResults=MAX_RESULTS,
        channelId=CHANNEL_ID,
    )

    response = request.execute()

    if not response["items"]:
        print_debug("[Search] No new episodes found. Exiting. ☹️")
        sys.exit()
    else:
        print_debug("[Search] New episode found! 🥳", response["items"][0]["snippet"]["title"])
        return response

def episode_exists():
    print_debug(f"[Episode_Exists] Checking if S{SEASON_NUMBER}E{EPISODE_NUMBER} exists in downloads folder.")
    # Search for file that contains season and episode number in /downloads directory
    import glob

    episode_files = glob.glob(f"downloads/*S{SEASON_NUMBER:02}E{EPISODE_NUMBER:02}*.mp4")

    if episode_files:
        print_debug(f"[Episode_Exists] Episode S{SEASON_NUMBER:02}E{EPISODE_NUMBER:02} already downloaded. Cancelling.")
        return True
    else:
        print_debug(f"[Episode_Exists] Episode S{SEASON_NUMBER:02}E{EPISODE_NUMBER:02} not found in downloads.")
        return False


def main():
    print_debug(f"[Main] Running downloader for {FILENAME}...")
    if episode_exists():
        print_debug(f"[Main] S{SEASON_NUMBER}E{EPISODE_NUMBER} already downloaded. Cancelling.")
        schedule.cancel_job(main)
        # Pause until next episode airs on Saturday at 4pm
        print_debug(f"[Main] Pausing until next episode airs on Saturday at 4pm...")
        if todays_day == "Saturday":
            print_debug(f"[Main] It's Saturday! Let's check the time...")
            if now.hour < 16:
                print_debug(f"[Main] It's not 4pm yet.")
            else:
                print_debug(f"[Main] It's 4pm! Proceeding with download.")
        else:
            print_debug(f"[Main] It's not Saturday.")
    else:
        print_debug(f"[Main] S{SEASON_NUMBER}E{EPISODE_NUMBER} not found in downloads. Proceeding with download.")

        try:
            print_debug(f"[Main] Searching for {QUERY}...")
            search_results = search()
        except ValueError:
            print("[Main] ⚠️ Invalid search value!")

        try:
            # verify that episode number in FILENAME matches the search_results episode number
            print_debug(
                f"[Main] Verify that episode number in FILENAME matches the search_results episode number."
            )
            try:
                search_results_episode_number = FILENAME.split("-")[1].split("E")[1].strip()
            except IndexError:
                print_debug("[Main] ⚠️ Invalid episode number!")
                sys.exit()

            if int(EPISODE_NUMBER) != int(search_results_episode_number):
                print_debug("[Main] ⚠️ Episode numbers do not match!")
                raise ValueError
            else:
                print_debug("[Main] ✅ Episode numbers match! Proceeding with download.")
        except ValueError:
            print_debug("[Main] Invalid episode number!")
            sys.exit()

        try:
            download(search_results)
        except ValueError:
            print_debug("[Main] ⚠️ Invalid download value!")

if __name__ == "__main__":
    print_debug(f"[Main] Startup...")
    main()
    
    if SCHEDULE == "@5min":
        print("[Schedule] Running every 5 minutes...")
        schedule.every(5).minutes.do(main)
    elif SCHEDULE == "@15min":
        print("[Schedule] Running every 15 minutes...")
        schedule.every(15).minutes.do(main)
    elif SCHEDULE == "@30min":
        print("[Schedule] Running every 30 minutes...")
        schedule.every(30).minutes.do(main)
    elif SCHEDULE == "@hourly":
        print("[Schedule] Running every hour...")
        schedule.every().hour.at(":00").do(main)
    elif SCHEDULE == "@daily":
        print("[Schedule] Running daily...")
        schedule.every().day.at("18:00").do(main)
    elif SCHEDULE == "@weekly":
        print("[Schedule] Running weekly...")
        schedule.every().saturday.at("18:00").do(main)
    else:
        print("[Schedule] ⚠️ Invalid SCHEDULE value!")
        sys.exit()

    while True:
        schedule.run_pending()
        
        n = schedule.idle_seconds()
        
        if n is None:
            # no more jobs
            break
        elif n > 0:
            if n <= 60:
                rounded_seconds = round(n)
                print_debug(f"[Main] Sleeping for {rounded_seconds} second(s)...")
            else:
                minutes = math.ceil(n / 60)
                seconds = n % 60
                print_debug(f"[Main] Sleeping for {minutes} minute(s)...")
            # sleep exactly the right amount of time
            time.sleep(n)
