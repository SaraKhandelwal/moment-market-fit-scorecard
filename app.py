import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Moment Market-Fit Scorecard", page_icon="📈", layout="wide")

AXES = {
    "predictability_window": "Predictability window",
    "binary_clarity": "Binary clarity",
    "time_to_reveal": "Time to reveal",
    "emotional_stakes": "Emotional stakes",
    "fanbase_precedent": "Fanbase precedent",
}

DEFAULT_WEIGHTS = {
    "predictability_window": 1.2,
    "binary_clarity": 1.2,
    "time_to_reveal": 1.0,
    "emotional_stakes": 1.1,
    "fanbase_precedent": 1.0,
}


@st.cache_data
def load_data(path="moment_scores.csv"):
    return pd.read_csv(path)


def compute_scores(df, weights):
    weight_sum = sum(weights.values())
    df = df.copy()
    df["composite_score"] = sum(df[axis] * w for axis, w in weights.items()) / weight_sum
    df["composite_score"] = df["composite_score"].round(2)
    return df.sort_values("composite_score", ascending=False).reset_index(drop=True)


if "custom_rows" not in st.session_state:
    st.session_state.custom_rows = []

base_df = load_data()

st.markdown(
    "<div style='letter-spacing:.14em;font-size:12px;color:#35d68c;text-transform:uppercase;'>"
    "MOMENT MARKET-FIT SCORECARD</div>",
    unsafe_allow_html=True,
)
st.title("Which live moments are worth a CRSH market?")
st.caption(
    "A live scoring tool for evaluating content formats on how well they fit a "
    "watch → predict → reveal mechanic. Adjust the weights, add your own formats, "
    "see the ranking shift in real time."
)

with st.container(border=True):
    st.markdown(
        "**The question:** which kinds of live moments are predictable-but-uncertain "
        "enough to make a good prediction market — and what does that say about which "
        "creators or formats to prioritize next?"
    )

tab1, tab2, tab3 = st.tabs(["Ranking", "Format profile", "Score your own"])

with tab1:
    st.markdown("#### Adjust how much each axis matters")
    st.caption("Drag to reweight the model — the ranking updates live below.")

    weights = {}
    cols = st.columns(5)
    for col, (key, label) in zip(cols, AXES.items()):
        with col:
            weights[key] = st.slider(label, 0.5, 2.0, DEFAULT_WEIGHTS[key], 0.1, key=f"w_{key}")

    all_rows = pd.concat(
        [base_df, pd.DataFrame(st.session_state.custom_rows)], ignore_index=True
    ) if st.session_state.custom_rows else base_df

    scored = compute_scores(all_rows, weights)

    fig = px.bar(
        scored,
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
        height=max(320, 60 * len(scored)),
        margin=dict(l=0, r=10, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Full dataset")
    st.dataframe(
        scored[["format", "category", *AXES.keys(), "composite_score"]],
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    all_rows = pd.concat(
        [base_df, pd.DataFrame(st.session_state.custom_rows)], ignore_index=True
    ) if st.session_state.custom_rows else base_df

    st.markdown("#### Compare format shapes, not just scores")
    st.caption("Two formats can score similarly but win for different reasons — this shows why.")

    picked = st.multiselect(
        "Pick formats to compare",
        all_rows["format"].tolist(),
        default=all_rows["format"].tolist()[:2],
    )

    if picked:
        fig2 = go.Figure()
        categories = list(AXES.values()) + [list(AXES.values())[0]]
        for fmt in picked:
            row = all_rows[all_rows["format"] == fmt].iloc[0]
            values = [row[k] for k in AXES.keys()] + [row[list(AXES.keys())[0]]]
            fig2.add_trace(go.Scatterpolar(r=values, theta=categories, fill="toself", name=fmt))
        fig2.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True,
            height=480,
            margin=dict(l=40, r=40, t=20, b=20),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Pick at least one format above.")

with tab3:
    st.markdown("#### Got a format in mind? Score it and see where it lands.")
    with st.form("new_format"):
        name = st.text_input("Format name", placeholder="e.g. Live trivia buzzer-beater")
        category = st.text_input("Category", placeholder="e.g. Game show style")
        c1, c2, c3, c4, c5 = st.columns(5)
        vals = {}
        with c1:
            vals["predictability_window"] = st.slider("Predictability", 1, 5, 3, key="new_pw")
        with c2:
            vals["binary_clarity"] = st.slider("Binary clarity", 1, 5, 3, key="new_bc")
        with c3:
            vals["time_to_reveal"] = st.slider("Time to reveal", 1, 5, 3, key="new_ttr")
        with c4:
            vals["emotional_stakes"] = st.slider("Emotional stakes", 1, 5, 3, key="new_es")
        with c5:
            vals["fanbase_precedent"] = st.slider("Fanbase precedent", 1, 5, 3, key="new_fp")
        notes = st.text_input("Notes (optional)", placeholder="Why does this fit?")
        submitted = st.form_submit_button("Add to scorecard")

        if submitted and name:
            new_row = {
                "format": name,
                "category": category or "Custom",
                **vals,
                "sample_source": "User submitted",
                "notes": notes,
            }
            st.session_state.custom_rows.append(new_row)
            st.success(f"Added '{name}' — check the Ranking tab to see where it lands.")

    if st.session_state.custom_rows:
        st.markdown("##### Your added formats")
        st.dataframe(pd.DataFrame(st.session_state.custom_rows), use_container_width=True, hide_index=True)
        if st.button("Clear my added formats"):
            st.session_state.custom_rows = []
            st.rerun()

st.divider()

st.markdown("### If I were CRSH: what I'd test next")
st.caption(
    "Three patterns worth checking against real event data — framed as tests, not claims, "
    "since I only have public engagement patterns to go on right now."
)

with st.container(border=True):
    st.markdown("**1. Time-to-reveal optimization**")
    st.markdown(
        "Shorter reveal windows likely tighten the feedback loop between predicting and "
        "seeing the result, which may drive more repeat participation even if individual "
        "bets are smaller.\n\n"
        "*Test:* compare markets under 3 min, 3 to 10 min, and 10+ min. Measure trades per "
        "user and repeat participation rate in each bucket."
    )

with st.container(border=True):
    st.markdown("**2. Emotional stakes vs binary clarity**")
    st.markdown(
        "Binary clarity likely gets people to place a first bet, but emotionally charged "
        "formats (eliminations, high-stakes reveals) may be what keeps them coming back, "
        "even when the outcome structure is less clean.\n\n"
        "*Test:* compare an esports-style structured format against an IRL/emotional format "
        "on engagement depth and volatility, not just initial trade volume."
    )

with st.container(border=True):
    st.markdown("**3. The predictability sweet spot**")
    st.markdown(
        "Highly predictable events probably reduce the incentive to trade, since the "
        "outcome feels obvious. Fully chaotic ones may reduce confidence to trade at all. "
        "The highest activity is likely in the middle band.\n\n"
        "*Test:* bucket past markets by implied odds distribution and check where trading "
        "volume actually peaks."
    )

st.markdown(
    "**Bottom line:** based on public engagement patterns, I'd prioritize short-duration, "
    "high-emotion formats first, but I'd want to validate all three of these against real "
    "CRSH data before treating any of them as settled."
)

st.divider()
st.markdown(
    "**How this was built:** scores are directional, based on public engagement patterns "
    "across TikTok/YouTube Shorts and Twitch clip culture — not CRSH's internal event or "
    "conversion data. Swap `moment_scores.csv` for real market-level metrics "
    "(time-to-lock, prediction volume, resolution rate by format) and everything above "
    "updates automatically. See `fetch_youtube_data.py` for a starting point on pulling "
    "real public engagement numbers."
)
