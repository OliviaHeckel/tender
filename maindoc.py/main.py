import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Weiterbildung Green Belt Ingolstadt", layout="wide")

# Root page acts as Home. Streamlit will automatically include it in the sidebar.

# Status: 0 = not started (red), 1 = in progress (yellow), 2 = done (green)

step_status = {
    "Requirements": 2,
    "Short List Suppliers": 1,
    "Proposals": 0,
    "Evaluation": 0,
    "Award": 0,
    "Contract": 0,
}

def get_status_icon(status):
    return {0: "🔴", 1: "🟡", 2: "🟢"}[status]

# ------------------ STYLING ------------------
st.markdown("""
<style>
.step-card {
    background-color: #ffffff;
    border: 1px solid #e6e9ef;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    min-height: 160px;
}
.step-title {
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 5px;
    color: #1f1f1f;
}
.step-date {
    font-size: 14px;
    color: #555;
    margin-top: 8px;
}
.status {
    font-size: 26px;
    margin-top: 10px;
}
/* Center the buttons under cards */
.stButton button {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.title("Vergabeprozess Weiterbildung Green Belt")

# Countdown Logic
sop_date = datetime(2026, 10, 30, 9, 0)
diff = sop_date - datetime.now()

if diff.total_seconds() > 0:
    st.info(f"🚀  Time until Start of Project (SOP): {diff.days} days, {diff.seconds // 3600} hours")
else:
    st.error("⚠️ SOP date has already passed")

st.divider()

# ------------------ NAVIGATION STEPS ------------------
st.text("Navigate through the procurement process steps:")
steps = [
    {"name": "Requirements", "date": "2026-03-15"},
    {"name": "Short List Suppliers", "date": "2026-04-20"},
    {"name": "Proposals", "date": "2026-06-25"},
    {"name": "Evaluation", "date": "2026-06-28"},
    {"name": "Award", "date": "2026-07-05"},
    {"name": "Contract", "date": "2026-07-15"},
]

cols = st.columns(len(steps))

for i, step in enumerate(steps):
    with cols[i]:
        status_icon = get_status_icon(step_status[step["name"]])

        # HTML CARD DISPLAY
        st.markdown(f"""
        <div class="step-card">
            <div class="step-title">{step['name']}</div>
            <div class="step-date">📅 Due: <b>{step['date']}</b></div>
            <div class="status">{status_icon}</div>
        </div>
        """, unsafe_allow_html=True)


