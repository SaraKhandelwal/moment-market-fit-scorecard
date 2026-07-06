import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="CRSH Creator Program: Market Analysis", page_icon="📊", layout="wide")

AXES = {
    "predictability_window": "Predictability Window",
    "binary_clarity": "Binary Clarity",
    "time_to_reveal": "Time to Reveal",
    "emotional_stakes": "Emotional Stakes",
    "fanbase_precedent": "Fanbase Precedent",
}

DEFAULT_WEIGHTS = {
    "predictability_window": 1.2,
    "binary_clarity": 1.2,
    "time_to_reveal": 1.0,
    "emotional_stakes": 1.1,
    "fanbase_precedent": 1.0,
}


@st.cache_data
def load_leaderboard(path="leaderboard.csv"):
    return pd.read_csv(path)


@st.cache_data
def load_moment_data(path="moment_scores.csv"):
    return pd.read_csv(path)


def compute_structural_score(df, weights):
    weight_sum = sum(weights.values())
    df = df.copy()
    df["structural_score"] = sum(df[axis] * w for axis, w in weights.items()) / weight_sum
    df["structural_score"] = df["structural_score"].round(2)
    return df


if "custom_rows" not in st.session_state:
    st.session_state.custom_rows = []

lb_df = load_leaderboard()
base_df = load_moment_data()

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown(
    "<div style='letter-spacing:.1em;font-size:12px;color:#5c8dd9;text-transform:uppercase;font-weight:600;'>"
    "PREPARED ANALYSIS — CRSH CREATOR PROGRAM</div>",
    unsafe_allow_html=True,
)
st.title("Market Format & Creator Prioritization Analysis")
st.caption(
    "Analysis of CRSH's Bronze League leaderboard data and live market chat, combined "
    "with third-party engagement benchmarks and a scoring model, to inform which stream "
    "formats and creator profiles the Creator Program should prioritize."
)

with st.container(border=True):
    st.markdown("**Objective**")
    st.markdown(
        "Determine which live-moment formats generate the participant volume and "
        "engagement that CRSH's creator payout brackets are designed to reward, and "
        "translate that into concrete creator-scouting criteria."
    )

st.divider()

tab0, tab1, tab2, tab3, tab4 = st.tabs(
    [
        "1. Platform Data Findings",
        "2. Market Benchmarks",
        "3. Format Scoring Model",
        "4. Test a Format",
        "5. Methodology",
    ]
)

# ---------------------------------------------------------------------------
# TAB 0 — Real platform data
# ---------------------------------------------------------------------------
with tab0:
    st.subheader("Finding 1: Accuracy and Trading Volume Are Inversely Related")
    st.markdown(
        "Data source: Bronze League leaderboard, 25 players, transcribed directly from "
        "the platform. No estimation applied."
    )

    corr = lb_df[["accuracy", "volume", "xp"]].corr()
    acc_vol_corr = corr.loc["accuracy", "volume"]
    high_acc = lb_df[lb_df.accuracy >= 80]
    low_acc = lb_df[lb_df.accuracy < 60]

    fig0 = px.scatter(
        lb_df,
        x="accuracy",
        y="volume",
        size="xp",
        hover_name="player",
        color="xp",
        color_continuous_scale=["#8a99a0", "#35a3d6"],
        labels={"accuracy": "Accuracy (%)", "volume": "Volume ($)", "xp": "XP"},
    )
    fig0.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=420,
        margin=dict(l=0, r=10, t=10, b=10),
    )
    st.plotly_chart(fig0, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Accuracy–Volume Correlation", f"{acc_vol_corr:.2f}")
    c2.metric("Avg. Volume, Accuracy ≥ 80%", f"${high_acc.volume.mean():.2f}")
    c3.metric("Avg. Volume, Accuracy < 60%", f"${low_acc.volume.mean():.2f}")

    st.markdown("**Interpretation**")
    st.markdown(
        f"Accuracy and volume show a strong negative correlation ({acc_vol_corr:.2f}) "
        f"across the sample. Players below 60% accuracy trade "
        f"{low_acc.volume.mean()/high_acc.volume.mean():.1f}x the volume of players "
        f"above 80% accuracy, and earn a higher average XP total "
        f"({low_acc.xp.mean():.0f} vs. {high_acc.xp.mean():.0f}) despite the lower "
        f"accuracy. The current XP structure is rewarding trading activity more than "
        f"predictive accuracy."
    )

    st.markdown("**Implication for creator payout brackets**")
    st.markdown(
        "Bracket eligibility is defined by CRSH-side viewers, unique participants, and "
        "integrity review — all activity-based measures, not accuracy-based ones. If "
        "revenue share follows the same pattern as XP, streams that attract a larger, "
        "less certain audience willing to bet on ambiguous outcomes may generate more "
        "revenue-share value than streams with a smaller, more accurate audience. This "
        "should be verified against actual payout data before it informs creator "
        "approval criteria; it is presented here as a testable hypothesis, not a "
        "conclusion."
    )

    with st.expander("View source data"):
        st.dataframe(lb_df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Finding 2: Short Reveal Windows Correspond to Measurable Chat Spikes")
    st.markdown(
        "Data source: live chat transcript from a market that resolved on a last-minute "
        "outcome reversal (two scoring events inside 60 seconds)."
    )
    st.markdown(
        "Message volume and emotional intensity in the transcript peaked in the two to "
        "three minutes surrounding the reveal, then declined. Message content included "
        "immediate reactions, disagreement over the outcome, and informal language "
        "consistent with high engagement. This is a direct, observed instance of the "
        "short-reveal-window effect referenced in the scoring model (Tab 3), rather than "
        "an assumption carried over from general content research."
    )
    st.caption(
        "Full transcript available on request. Informal/profane language has been "
        "summarized rather than reproduced here."
    )

# ---------------------------------------------------------------------------
# TAB 1 — Proxy engagement benchmarks
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("Third-Party Engagement Benchmarks by Content Category")
    st.markdown(
        "No published benchmark exists for engagement by prediction-market mechanic "
        "(e.g., reveal vs. clutch vs. challenge). Each CRSH-relevant format below is "
        "therefore mapped to its closest published content-niche benchmark. This "
        "mapping is a judgment call and is disclosed per row. Where no benchmark could "
        "be isolated for a category, the value is left blank rather than estimated."
    )

    plot_df = base_df.dropna(subset=["cited_engagement_rate"]).sort_values(
        "cited_engagement_rate", ascending=True
    )
    fig = px.bar(
        plot_df,
        x="cited_engagement_rate",
        y="format",
        orientation="h",
        color="cited_engagement_rate",
        color_continuous_scale=["#8a99a0", "#35a3d6"],
        text="cited_engagement_rate",
        labels={"cited_engagement_rate": "Engagement Rate % (Proxy Niche)", "format": ""},
    )
    fig.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=max(300, 55 * len(plot_df)),
        margin=dict(l=0, r=10, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    missing = base_df[base_df["cited_engagement_rate"].isna()]
    if len(missing):
        st.info(
            "No isolated published rate identified for: "
            + ", ".join(missing["format"].tolist())
            + "."
        )

    st.markdown("**Source data**")
    st.dataframe(
        base_df[["format", "proxy_niche", "cited_engagement_rate", "source", "notes"]],
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------------------------------------------------------
# TAB 2 — Structural fit model
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("Structural Fit Model")
    st.markdown(
        "This model scores each format on five criteria for fit with the watch-predict-"
        "reveal mechanic. It is a qualitative estimate, distinct from the engagement "
        "data in Tab 1. Weights are adjustable below to test sensitivity to different "
        "assumptions."
    )

    weights = {}
    cols = st.columns(5)
    for col, (key, label) in zip(cols, AXES.items()):
        with col:
            weights[key] = st.slider(label, 0.5, 2.0, DEFAULT_WEIGHTS[key], 0.1, key=f"w_{key}")

    all_rows = pd.concat(
        [base_df, pd.DataFrame(st.session_state.custom_rows)], ignore_index=True
    ) if st.session_state.custom_rows else base_df

    scored = compute_structural_score(all_rows, weights).sort_values(
        "structural_score", ascending=False
    ).reset_index(drop=True)

    fig2 = px.bar(
        scored,
        x="structural_score",
        y="format",
        orientation="h",
        color="structural_score",
        color_continuous_scale=["#8a99a0", "#4d8fff"],
        text="structural_score",
        labels={"structural_score": "Structural Fit Score (/5)", "format": ""},
    )
    fig2.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=max(320, 60 * len(scored)),
        margin=dict(l=0, r=10, t=10, b=10),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**Format comparison**")
    picked = st.multiselect(
        "Select formats to compare",
        all_rows["format"].tolist(),
        default=all_rows["format"].tolist()[:2],
    )
    if picked:
        fig3 = go.Figure()
        categories = list(AXES.values()) + [list(AXES.values())[0]]
        for fmt in picked:
            row = all_rows[all_rows["format"] == fmt].iloc[0]
            values = [row[k] for k in AXES.keys()] + [row[list(AXES.keys())[0]]]
            fig3.add_trace(go.Scatterpolar(r=values, theta=categories, fill="toself", name=fmt))
        fig3.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True,
            height=460,
            margin=dict(l=40, r=40, t=20, b=20),
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    st.subheader("Creator Scouting Criteria")
    st.markdown(
        "Derived from the findings above, the following criteria are proposed for "
        "identifying creator applicants, rather than specific individuals:"
    )
    st.markdown(
        "- **Audience tier:** approximately 500–15,000 concurrent viewers. This matches "
        "the Starter payout bracket's economics and provides room for creators to "
        "grow within the program, rather than targeting established creators whose "
        "scale and existing brand agreements make Starter-tier terms impractical.\n"
        "- **Content category:** IRL/challenge streams and sports-reaction content, "
        "based on the highest proxy engagement rates identified in Tab 1, followed by "
        "competitive gaming for its high emotional-stakes and fanbase-precedent scores "
        "in the structural model.\n"
        "- **Pre-existing chat behavior:** streams where viewers already react quickly "
        "and disagree over outcomes in chat, prior to any CRSH market being introduced. "
        "This is a direct, observable indicator of the volume-driving behavior "
        "identified in Finding 1."
    )

# ---------------------------------------------------------------------------
# TAB 3 — Score your own format
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("Test a New Format Against the Model")
    st.markdown(
        "Scores structural fit only. No engagement-rate benchmark can be generated for "
        "a hypothetical format without a live data source."
    )
    with st.form("new_format"):
        name = st.text_input("Format name")
        category = st.text_input("Category")
        c1, c2, c3, c4, c5 = st.columns(5)
        vals = {}
        with c1:
            vals["predictability_window"] = st.slider("Predictability", 1, 5, 3, key="new_pw")
        with c2:
            vals["binary_clarity"] = st.slider("Binary Clarity", 1, 5, 3, key="new_bc")
        with c3:
            vals["time_to_reveal"] = st.slider("Time to Reveal", 1, 5, 3, key="new_ttr")
        with c4:
            vals["emotional_stakes"] = st.slider("Emotional Stakes", 1, 5, 3, key="new_es")
        with c5:
            vals["fanbase_precedent"] = st.slider("Fanbase Precedent", 1, 5, 3, key="new_fp")
        notes = st.text_input("Notes (optional)")
        submitted = st.form_submit_button("Add to Model")

        if submitted and name:
            new_row = {
                "format": name,
                "category": category or "Custom",
                "proxy_niche": None,
                "cited_engagement_rate": None,
                "source": "User submitted — no engagement benchmark",
                **vals,
                "notes": notes,
            }
            st.session_state.custom_rows.append(new_row)
            st.success(f"'{name}' added. See Tab 3 ranking for placement.")

    if st.session_state.custom_rows:
        st.markdown("**Submitted formats**")
        st.dataframe(pd.DataFrame(st.session_state.custom_rows), use_container_width=True, hide_index=True)
        if st.button("Clear submitted formats"):
            st.session_state.custom_rows = []
            st.rerun()

# ---------------------------------------------------------------------------
# TAB 4 — Methodology / evidence base
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("Methodology and Evidence Base")

    st.markdown("**Scoring axis rationale**")
    with st.container(border=True):
        st.markdown("*Predictability Window & Time to Reveal*")
        st.markdown(
            "Short-form video completion rates are consistently higher than long-form: "
            "60–90% for short-form versus 35–50% for longer content, with roughly a "
            "third of short videos watched to near completion. Viewer retention "
            "decisions occur within the first few seconds of playback."
        )
        st.caption("Sources: Socialinsider Video Metrics Guide; Marketing LTB Short-Form Video Statistics, 2026")

    with st.container(border=True):
        st.markdown("*Binary Clarity & Emotional Stakes*")
        st.markdown(
            "Grounded in information gap theory (Loewenstein, 1994): curiosity is "
            "driven by a perceived gap between known and desired information, and "
            "motivation to close that gap scales with prior investment in the topic."
        )
        st.caption("Source: Loewenstein, G. (1994), The Psychology of Curiosity")

    with st.container(border=True):
        st.markdown("*Fanbase Precedent*")
        st.markdown(
            "Grounded in the Zeigarnik effect: unfinished or open-loop information is "
            "retained and engaged with more than resolved information. Existing "
            "fanbases already practice this engagement pattern with a given creator."
        )
        st.caption("Source: Zeigarnik, B. (1927/1938)")

    st.markdown("**Data limitations**")
    st.markdown(
        "- Engagement-rate figures in Tab 1 are drawn from general content-niche "
        "benchmarks, not from CRSH's own market or creator data.\n"
        "- Structural fit scores in Tab 2 are qualitative estimates informed by the "
        "research above, not measured outcomes.\n"
        "- Leaderboard analysis in Tab 0 reflects 25 visible Bronze League entries at a "
        "single point in time and has not been tested for statistical significance "
        "beyond the correlation reported."
    )

    st.markdown("**Recommended validation steps**")
    st.markdown(
        "1. Compare trades-per-user and repeat participation across markets with "
        "reveal windows under 3 minutes, 3–10 minutes, and over 10 minutes.\n"
        "2. Compare engagement depth and volatility between structured "
        "(e.g., esports) and emotionally-driven (e.g., IRL) formats.\n"
        "3. Bucket historical markets by implied odds distribution to identify where "
        "trading volume actually peaks.\n"
        "4. Cross-reference actual creator revenue-share payouts against viewer "
        "accuracy distribution to test whether bracket criteria should weight "
        "participant volume over resolved accuracy."
    )
