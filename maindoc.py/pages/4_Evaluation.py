
import streamlit as st
import pandas as pd
import os

import streamlit as st

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Training Evaluation",
    page_icon="🎯",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎯 Training Evaluation Tool")
st.write("Rate each criterion from 1 (poor) to 10 (excellent). Scores are weighted automatically.")
st.divider()

# ── Criteria Definition ───────────────────────────────────────────────────────
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
    st.subheader("📋 Evaluation Criteria")
    
    scores = {}
    
    # Render sliders using clean native configurations
    for c in criteria:
        weight_pct = f"{int(c['weight'] * 100)}%"
        scores[c["key"]] = st.slider(
            label=f"{c['icon']} {c['label']} (Weight: {weight_pct})",
            min_value=1,
            max_value=10,
            value=5,
            step=1,
            help=c["help"],
            key=c["key"],
        )
    
    st.divider()
    st.subheader("💬 Comments")
    comment = st.text_area(
        label="Additional Comments (optional)",
        placeholder="Share any further thoughts about this training offer…",
        height=110,
    )
    
    submitted = st.form_submit_button("Calculate Weighted Score")

# ── Results Execution ─────────────────────────────────────────────────────────
if submitted:
    weighted_total = sum(
        scores[c["key"]] * c["weight"] for c in criteria
    )
    
    st.divider()
    st.subheader("📊 Score Breakdown")
    
    # Display performance metrics across columns natively
    cols = st.columns(len(criteria))
    for col, c in zip(cols, criteria):
        raw = scores[c["key"]]
        contrib = raw * c["weight"]
        col.metric(
            label=f"{c['icon']} {c['label']}",
            value=f"{raw}/10",
            delta=f"+{contrib:.2f} pts",
        )
        
    st.divider()
    st.subheader("🔎 Supplier Recommendation Summary")
    st.write(f"### Weighted Total Score: **{weighted_total:.2f} / 10.00**")
    
    # Map the score verdicts to native alert components matching 1_Requirements.py
    if weighted_total >= 8:
        st.success("✅ **Highly Recommended**")
    elif weighted_total >= 6:
        st.warning("⚠️ **Conditionally Recommended**")
    else:
        st.error("❌ **Not Recommended**")
        
    if comment.strip():
        st.info(f"📝 **Your comment:** {comment}")
        
    st.success("Evaluation completed successfully! Adjust the inputs above to recalculate at any time.")
