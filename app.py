import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Moment Market-Fit Scorecard", page_icon="📈", layout="wide")

AXES = {
    "predictability_window": "Predictability window",
    "binary_clarity": "Binary clarity",
    "time_to_reveal": "Time to reveal",
    "emotional_stakes": "Emotional stakes",
    "fanbase_precedent": "Fanbase precedent",
}

WEIGHTS = {
    "predictability_window": 1.2,
    "binary_clarity": 1.2,
    "time_to_reveal": 1.0,
    "emotional_stakes": 1.1,
    "fanbase_precedent": 1.0,
}


@st.cache_data
def load_data(path="moment_scores.csv"):
    df = pd.read_csv(path)
    weight_sum = sum(WEIGHTS.values())
    df["composite_score"] = sum(df[axis] * w for axis, w in WEIGHTS.items()) / weight_sum
    df["composite_score"] = df["composite_score"].round(2)
    return df.sort_values("composite_score", ascending=False).reset_index(drop=True)


df = load_data()

st.markdown(
    "<div style='letter-spacing:.14em;font-size:12px;color:#35d68c;text-transform:uppercase;'>"
    "MOMENT MARKET-FIT SCORECARD</div>",
    unsafe_allow_html=True,
)
st.title("Which live moments are worth a CRSH market?")
st.caption(
    "A scoring framework for evaluating content formats on how well they fit a "
    "watch → predict → reveal mechanic, using public engagement patterns as a stand-in "
    "for real platform data."
)

with st.container(border=True):
    st.markdown(
        "**The question:** which kinds of live moments are predictable-but-uncertain "
        "enough to make a good prediction market — and what does that say about which "
        "creators or formats to prioritize next?"
    )

st.markdown("### Format ranking")
fig = px.bar(
    df,
    x="composite_score",
    y="format",
    orientation="h",
    color="composite_score",
    color_continuous_scale=["#8a99a0", "#35d68c"],
    text="composite_score",
    labels={"composite_score": "Composite score (/5)", "format": ""},
)
fig.update_layout(
    yaxis={"categoryorder": "total ascending"},
    coloraxis_showscale=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    height=380,
    margin=dict(l=0, r=10, t=10, b=10),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Score breakdown by axis")
selected = st.selectbox("Inspect a format", df["format"])
row = df[df["format"] == selected].iloc[0]

cols = st.columns(5)
for col, (key, label) in zip(cols, AXES.items()):
    col.metric(label, f"{row[key]} / 5")

st.caption(f"**Notes:** {row['notes']}  ·  Source pattern: {row['sample_source']}")

st.markdown("### Full dataset")
st.dataframe(
    df[["format", "category", *AXES.keys(), "composite_score"]],
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.markdown(
    "**How this was built:** scores are directional, based on public engagement patterns "
    "across TikTok/YouTube Shorts and Twitch clip culture — not CRSH's internal event or "
    "conversion data. Swap `moment_scores.csv` for real market-level metrics "
    "(time-to-lock, prediction volume, resolution rate by format) and the ranking updates "
    "automatically. See `fetch_youtube_data.py` for a starting point on pulling real public "
    "engagement numbers with the YouTube Data API."
)
