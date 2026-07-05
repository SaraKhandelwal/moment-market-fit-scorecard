# Moment Market-Fit Scorecard

A scoring framework for ranking live content formats (reveal clips, challenges,
gaming clutch moments, etc.) on how well they fit a watch → predict → reveal
prediction-market mechanic : built as a proof-of-concept dashboard.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy for free (Streamlit Community Cloud)
1. Push this folder to a new GitHub repo (public).
2. Go to https://share.streamlit.io → "New app" → connect your GitHub repo.
3. Set the main file to `app.py`. Deploy. You'll get a public URL in ~2 minutes.

## Files
- `app.py` : the Streamlit dashboard
- `moment_scores.csv` : manually-scored dataset (5 axes, 1-5 scale) per format
- `fetch_youtube_data.py` : optional script to pull *real* public engagement
  numbers via the YouTube Data API, to sanity-check the manual scores. Requires
  your own free API key, set as an environment variable : never commit a key
  to the repo.

## Scoring methodology
Each format is scored 1-5 on five axes:
- **Predictability window** : is there a clear "before" moment ahead of the outcome?
- **Binary clarity** : does the outcome resolve cleanly (yes/no, A/B)?
- **Time to reveal** : short enough to hold live attention?
- **Emotional stakes** : does the audience care who's right?
- **Fanbase precedent** : already proven to spread on TikTok/Twitch/YouTube?

Composite score is a weighted average (weights in `app.py`). Swap in real
market-level data (time-to-lock, prediction volume, resolution rate) and the
ranking updates automatically, no code changes needed, just replace the CSV.

## Honest scope note
The current dataset is directional, based on public content patterns, not
CRSH's internal data. This is meant as a framework to test against real
numbers, not a finished analysis.
