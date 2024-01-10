# Zvezde Granda Downloader

Downloads newest episode uploaded.

| parameter          | required | type   | default                                            |
| ------------------ | -------- | ------ | -------------------------------------------------- |
| API_KEY            | yes      | string | ""                                                 |
| START_DATE         | yes      | string | "2023-09-23"                                       |
| CHANNEL_ID         | yes      | string | ""                                                 |
| TIMEZONE           | no       | string | "US/Central"                                       |
| SLACK_WEBHOOK      | no       | string | ""                                                 |
| VIDEO_DATE         | no       | string | "DD.MM.YYYY"                                       |
| QUERY              | no       | string | "Zvezde Granda - Cela emisija S15E01 - DD.MM.YYYY" |
| EPISODE_ADJUSTMENT | no       | string | 1                                                  |
| EPISODE_NUMBER     | no       | string | "weeks_since_start_date + episode_adjustmen"       |
| SEASON_NUMBER      | no       | string | "start_date_year - 2008"                           |

```bash
docker run --rm \
    # --pull=always \
    --name="zvezde-granda-downloader" \
    -e API_KEY="***INSERT_API_KEY_HERE***" \
    -e CHANNEL_ID="***INSERT_YOUTUBE_CHANNEL_ID***" \
    -e SLACK_WEBHOOK="***INSERT_SLACK_WEBHOOK_HERE***" \
    -e VIDEO_DATE="25.11.2023" \
    -v "/local/folder/show/season/:/usr/src/app/downloads" \
    subasically/zvezde-granda-downloader:main
```
