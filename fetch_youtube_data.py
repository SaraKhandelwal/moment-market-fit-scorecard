"""
Optional: pull real public engagement numbers for each moment format using the
YouTube Data API v3, instead of relying on the manually-scored CSV.

Setup:
1. Get a free API key: https://console.cloud.google.com/apis/credentials
   (enable "YouTube Data API v3" on the project first)
2. Set it as an environment variable so it never gets committed to GitHub:
       export YOUTUBE_API_KEY="your_key_here"
3. Run:  python fetch_youtube_data.py

This searches for a handful of videos per format category, pulls view/like/comment
counts, and writes an "engagement_rate" column you can blend into moment_scores.csv
as a real-world sanity check on the manual scores.

NOTE: this does not run automatically inside the deployed Streamlit app — API keys
should never be public. Run it locally, review the output, then decide whether to
update moment_scores.csv with anything it surfaces.
"""

import os
import time
import pandas as pd
import requests

API_KEY = os.environ.get("YOUTUBE_API_KEY")
BASE_SEARCH = "https://www.googleapis.com/youtube/v3/search"
BASE_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"

QUERIES = {
    "Reveal / payoff": "wait for it reveal shorts",
    "Live challenge outcome": "can he clear it challenge stream",
    "Clutch gaming moment": "clutch play highlight stream",
    "Stunt / dare bet": "streamer dare bet irl",
    "1v1 creator matchup": "creator 1v1 battle",
    "Q&A prediction game": "guess the answer game show",
}


def search_videos(query, max_results=5):
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": "viewCount",
        "key": API_KEY,
    }
    r = requests.get(BASE_SEARCH, params=params, timeout=10)
    r.raise_for_status()
    return [item["id"]["videoId"] for item in r.json().get("items", [])]


def get_stats(video_ids):
    params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
    r = requests.get(BASE_VIDEOS, params=params, timeout=10)
    r.raise_for_status()
    return r.json().get("items", [])


def main():
    if not API_KEY:
        raise SystemExit("Set YOUTUBE_API_KEY as an environment variable first.")

    rows = []
    for category, query in QUERIES.items():
        ids = search_videos(query)
        if not ids:
            continue
        for item in get_stats(ids):
            stats = item.get("statistics", {})
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
            engagement_rate = (likes + comments) / views if views else 0
            rows.append(
                {
                    "category": category,
                    "video_id": item["id"],
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "engagement_rate": round(engagement_rate, 5),
                }
            )
        time.sleep(0.2)  # be polite to the API

    out = pd.DataFrame(rows)
    out.to_csv("youtube_engagement_raw.csv", index=False)
    print(out.groupby("category")["engagement_rate"].mean().sort_values(ascending=False))
    print("\nSaved raw data to youtube_engagement_raw.csv")


if __name__ == "__main__":
    main()
