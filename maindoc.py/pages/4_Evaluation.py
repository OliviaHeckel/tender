
import streamlit as st
import pandas as pd
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Training Evaluation",
    page_icon="🎯",
    layout="centered",
)
 
# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
 
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}
 
/* Dark background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e);
    color: #e8e8f0;
}
 
/* Header banner */
.header-banner {
    background: linear-gradient(90deg, #6c63ff 0%, #3ec6e0 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 32px;
    box-shadow: 0 8px 32px rgba(108, 99, 255, 0.4);
}
.header-banner h1 {
    margin: 0 0 6px 0;
    font-size: 2rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.5px;
}
.header-banner p {
    margin: 0;
    color: rgba(255,255,255,0.85);
    font-size: 0.95rem;
    font-weight: 300;
}
 
/* Criterion card */
.criterion-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 22px 26px 10px 26px;
    margin-bottom: 20px;
    backdrop-filter: blur(8px);
    transition: border-color 0.2s;
}
.criterion-card:hover {
    border-color: rgba(108, 99, 255, 0.5);
}
.criterion-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.criterion-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #fff;
}
.criterion-weight {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    background: linear-gradient(90deg, #6c63ff, #3ec6e0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 3px 10px;
    border: 1px solid rgba(108, 99, 255, 0.4);
    border-radius: 20px;
    -webkit-text-fill-color: unset;
    color: #a89cff;
}
 
/* Score result box */
.score-box {
    background: linear-gradient(135deg, rgba(108,99,255,0.25), rgba(62,198,224,0.15));
    border: 1px solid rgba(108, 99, 255, 0.5);
    border-radius: 16px;
    padding: 28px 32px;
    text-align: center;
    margin-top: 10px;
}
.score-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #6c63ff, #3ec6e0);
    -webkit-background-clip: text;
    color: transparent;
}
.score-label {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.6);
    margin-top: 4px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.verdict {
    font-size: 1.2rem;
    font-weight: 600;
    margin-top: 14px;
    padding: 8px 20px;
    border-radius: 30px;
    display: inline-block;
}
 
/* Streamlit widget overrides */
div[data-testid="stSlider"] > div {
    padding-top: 4px;
}
label[data-testid="stWidgetLabel"] {
    color: rgba(255,255,255,0.7) !important;
    font-size: 0.85rem !important;
}
 
/* Submit button */
div.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #6c63ff, #3ec6e0);
    color: white;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    border: none;
    border-radius: 12px;
    padding: 14px;
    cursor: pointer;
    transition: opacity 0.2s, transform 0.1s;
    margin-top: 8px;
}
div.stButton > button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)
 
# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <h1>🎯 Training Evaluation Form</h1>
    <p>Rate each criterion from 1 (poor) to 10 (excellent). Scores are weighted automatically.</p>
</div>
""", unsafe_allow_html=True)
 
# ── Criteria definition ───────────────────────────────────────────────────────
criteria = [
    {
        "key":    "preis",
        "label":  "Preis",
        "weight": 0.30,
        "icon":   "💶",
        "help":   "How competitive and fair is the pricing for this training?",
    },
    {
        "key":    "trainer_expertise",
        "label":  "Trainer Expertise",
        "weight": 0.25,
        "icon":   "🧑‍🏫",
        "help":   "How experienced and knowledgeable is the trainer in this field?",
    },
    {
        "key":    "industry_alignment",
        "label":  "Industry Alignment",
        "weight": 0.20,
        "icon":   "🏭",
        "help":   "How well does the content align with current industry needs?",
    },
    {
        "key":    "training_duration",
        "label":  "Training Duration",
        "weight": 0.15,
        "icon":   "⏱️",
        "help":   "Is the duration appropriate for the depth of content covered?",
    },
    {
        "key":    "certification",
        "label":  "Certification",
        "weight": 0.10,
        "icon":   "🏅",
        "help":   "How valuable and recognised is the certification provided?",
    },
]
 
# ── Form ──────────────────────────────────────────────────────────────────────
with st.form("evaluation_form"):
 
    scores = {}
 
    for c in criteria:
        weight_pct = f"{int(c['weight'] * 100)}%"
        st.markdown(f"""
        <div class="criterion-card">
            <div class="criterion-header">
                <span class="criterion-title">{c['icon']} &nbsp;{c['label']}</span>
                <span class="criterion-weight">Weight: {weight_pct}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
 
        scores[c["key"]] = st.slider(
            label=f"Score for {c['label']}",
            min_value=1,
            max_value=10,
            value=5,
            step=1,
            help=c["help"],
            key=c["key"],
        )
        st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)
 
    # Optional comment
    st.markdown("<br>", unsafe_allow_html=True)
    comment = st.text_area(
        "💬 Additional Comments (optional)",
        placeholder="Share any further thoughts about this training offer…",
        height=110,
    )
 
    submitted = st.form_submit_button("Calculate Weighted Score →")
 
# ── Results ───────────────────────────────────────────────────────────────────
if submitted:
    weighted_total = sum(
        scores[c["key"]] * c["weight"] for c in criteria
    )
 
    # Build per-criterion breakdown
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Score Breakdown")
 
    cols = st.columns(len(criteria))
    for col, c in zip(cols, criteria):
        raw   = scores[c["key"]]
        contrib = raw * c["weight"]
        col.metric(
            label=f"{c['icon']} {c['label']}",
            value=f"{raw}/10",
            delta=f"+{contrib:.2f} pts",
        )
 
    # Overall verdict
    if weighted_total >= 8:
        verdict_html = '<span class="verdict" style="background:rgba(62,224,130,0.2);color:#3ee082;">✅ Highly Recommended</span>'
    elif weighted_total >= 6:
        verdict_html = '<span class="verdict" style="background:rgba(255,200,60,0.2);color:#ffc83c;">⚠️ Conditionally Recommended</span>'
    else:
        verdict_html = '<span class="verdict" style="background:rgba(255,80,80,0.2);color:#ff5050;">❌ Not Recommended</span>'
 
    st.markdown(f"""
    <div class="score-box">
        <div class="score-value">{weighted_total:.2f}</div>
        <div class="score-label">Weighted Total Score (out of 10)</div>
        {verdict_html}
    </div>
    """, unsafe_allow_html=True)
 
    if comment.strip():
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"📝 **Your comment:** {comment}")
 
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("Evaluation submitted successfully! You can adjust the sliders and re-submit at any time.")
