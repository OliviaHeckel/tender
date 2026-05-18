
import streamlit as st
import pandas as pd
import os

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Training Evaluation",
    page_icon="🎯",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎯 Supplier Training Evaluation Tool")
st.write("Select a supplier from your filtered RFQ list and rate them from 1 (poor) to 10 (excellent).")
st.divider()

# ── Load Filtered Suppliers ───────────────────────────────────────────────────
# Matches the exact filename output from 1_Requirements.py
csv_path = "filtered_supliers.csv" 

if os.path.exists(csv_path):
    try:
        df_suppliers = pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        df_suppliers = pd.DataFrame()
else:
    df_suppliers = pd.DataFrame()

# Guard clause if the RFQ generator hasn't been run yet
if df_suppliers.empty:
    st.warning("⚠️ No filtered suppliers found. Please run the RFQ Generator first to create the `filtered_supliers.csv` file.")
    st.stop()

# ── Supplier Selection ────────────────────────────────────────────────────────
st.subheader("🏢 Supplier Selection")
supplier_names = sorted(df_suppliers["Supplier Name"].unique().tolist())
selected_supplier = st.selectbox("Choose a supplier to evaluate:", options=supplier_names)

# Fetch details for the selected supplier to display as context
supplier_data = df_suppliers[df_suppliers["Supplier Name"] == selected_supplier].iloc[0]

col_inf1, col_inf2 = st.columns(2)
with col_inf1:
    st.write(f"**Contact Email:** {supplier_data.get('Contact Email', 'N/A')}")
    st.write(f"**Participants Limit:** {supplier_data.get('Participants per Session', 'N/A')}")
with col_inf2:
    st.write(f"**Delivery Mode Available:** {supplier_data.get('Delivery Mode', 'N/A')}")
    st.write(f"**Languages:** {supplier_data.get('Languages Available', 'N/A')}")

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

# ── Evaluation Form ───────────────────────────────────────────────────────────
with st.form("evaluation_form"):
    st.subheader(f"📋 Score Card: {selected_supplier}")
    
    scores = {}
    
    # Render sliders dynamically
    for c in criteria:
        weight_pct = f"{int(c['weight'] * 100)}%"
        scores[c["key"]] = st.slider(
            label=f"{c['icon']} {c['label']} (Weight: {weight_pct})",
            min_value=1,
            max_value=10,
            value=5,
            step=1,
            help=c["help"],
            key=f"{selected_supplier}_{c['key']}", # Unique key per supplier selection
        )
    
    st.divider()
    st.subheader("💬 Evaluation Notes")
    comment = st.text_area(
        label="Additional Comments (optional)",
        placeholder=f"Share any further thoughts regarding the offer from {selected_supplier}…",
        height=110,
    )
    
    submitted = st.form_submit_button(f"Calculate Weighted Score for {selected_supplier}")

# ── Results Execution ─────────────────────────────────────────────────────────
