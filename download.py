from __future__ import unicode_literals

import yt_dlp
import save_file
import notification
import sys

def video(response, FILENAME, FORMAT, WEBHOOK, SEASON_NUMBER, EPISODE_NUMBER, todays_date):
    ydl_options = {
        "outtmpl": "downloads/" + FILENAME, 
        "format": FORMAT, 
        "quiet": False,
        }
    ydl = yt_dlp.YoutubeDL(ydl_options)

    for item in response["items"]:
        video_url = "http://www.youtube.com/watch?v=" + item["id"]["videoId"]
        thumbnail_url = item["snippet"]["thumbnails"]["high"]["url"]
        thumb_max_url = thumbnail_url.replace("hqdefault", "maxresdefault")

        print("Downloading thumbnail", f"{FILENAME}.png")
        save_file.thumbnail(thumb_max_url, f"{FILENAME}.png")

        print("Downloading", FILENAME)
        # ydl.download(video_url)

        if WEBHOOK:
            print("Sending notification to Slack")
            notification.slack(
                WEBHOOK, "New Episode! ✌️", FILENAME, thumb_max_url
            )
            
            print("Updating downloads_history.csv")
            # Update downloads_history.csv with new line for the new episode
            with open("downloads/downloads_history.csv", "a") as file:
                file.write(
                    f"{SEASON_NUMBER},{EPISODE_NUMBER},{todays_date}\n"
                )
        else:
            print("No Slack webhook provided. Notification will not be sent. Exiting.")
            sys.exit()
