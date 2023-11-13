import sys
from googleapiclient.discovery import build


def channel_videos(QUERY, API_KEY, CHANNEL_ID, MAX_RESULTS):
    print("Searching for new episodes...", QUERY)
    youtube = build("youtube", "v3", developerKey=API_KEY)

    request = youtube.search().list(
        part="snippet",
        q=QUERY,
        # type="video",
        maxResults=MAX_RESULTS,
        channelId=CHANNEL_ID,
    )

    response = request.execute()

    if not response["items"]:
        print("No new episodes :(")
        sys.exit()
    else:
        print("New episode found!", response["items"][0]["snippet"]["title"])
        return response
