from slack_sdk.webhook import WebhookClient

def slack(HEADING, IMG_NAME, IMG_URL):
    url = "https://hooks.slack.com/services/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"
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
