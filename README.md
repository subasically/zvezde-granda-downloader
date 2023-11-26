# Zvezde Granda Downloader

Downloads newest episode uploaded.

| parameter     | required | type   | default                                                           |
| ------------- | -------- | ------ | ----------------------------------------------------------------- |
| API_KEY       | yes      | string | ""                                                                |
| SLACK_WEBHOOK | no       | string | ""                                                                |
| VIDEO_DATE    | no       | string | "DD.MM.YYYY"                                                      |
| QUERY         | no       | string | "Zvezde Granda - Cela emisija {EPISODE_NUMBER:02} - {VIDEO_DATE}" |

```bash
docker run --rm \
    --pull=always \
    --name="zvezde-granda-downloader" \
    -e API_KEY="***INSERT_API_KEY_HERE***" \
    -e SLACK_WEBHOOK="***INSERT_SLACK_WEBHOOK_HERE***" \
    -e VIDEO_DATE="25.11.2023" \
    -v "/local/folder/show/season/:/usr/src/app/downloads" \
    subasically/zvezde-granda-downloader:main
```
