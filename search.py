import sys
from googleapiclient.discovery import build

def channel_videos(QUERY, API_KEY, PUBLISHED_AFTER, PUBLISHED_BEFORE,CHANNEL_ID, MAX_RESULTS):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    request = youtube.search().list(
        part="snippet",
        q=QUERY,
        type="video",
        publishedAfter=PUBLISHED_AFTER,
        publishedBefore=PUBLISHED_BEFORE,
        maxResults=MAX_RESULTS,
        channelId=CHANNEL_ID,
    )

    response = request.execute()

    if not response["items"]:
        print("Nothing found. :(")
        sys.exit()
    else:
        return response