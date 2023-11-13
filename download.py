import yt_dlp
import save_file
import notification
import sys


def video(response, FILENAME, FORMAT, WEBHOOK):
    ydl_options = {"outtmpl": "downloads/" + FILENAME, "format": FORMAT}
    ydl = yt_dlp.YoutubeDL(ydl_options)

    for item in response["items"]:
        video_url = "http://www.youtube.com/watch?v=" + item["id"]["videoId"]
        thumbnail_url = item["snippet"]["thumbnails"]["high"]["url"]
        thumb_max_url = thumbnail_url.replace("hqdefault", "maxresdefault")

        # print(thumb_max_url)
        save_file.thumbnail(thumb_max_url, FILENAME + ".png")

        print("Downloading", FILENAME)
        ydl.download(video_url)

        if WEBHOOK:
            notification.slack(
                WEBHOOK, "Zvezde Granda Downloader", FILENAME, thumb_max_url
            )
        else:
            print("No Slack webhook provided. Notification will not be sent. Exiting.")
            sys.exit()
