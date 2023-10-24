from slack_sdk.webhook import WebhookClient

def slack(WEBHOOK, HEADING, IMG_NAME, IMG_URL):
    if WEBHOOK:
        url = WEBHOOK
        webhook = WebhookClient(url)
        webhook.send(
            text="fallback",
            blocks= [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": HEADING,
                        "emoji": True
                    }
                },
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": IMG_NAME,
                        "emoji": True
                    },
                    "image_url": IMG_URL,
                    "alt_text": "marg"
                }
            ]
        )
    else:
        print("Missing webhook url!")
