import streamlit as st
import pandas as pd
import os

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supplier Comparison Matrix",
    page_icon="🎯",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎯 Supplier Comparison & Award Matrix")
st.write("Select 3 suppliers from your filtered RFQ list to evaluate them side-by-side. The final score will determine the award winner.")
st.divider()

# ── Load Filtered Suppliers ───────────────────────────────────────────────────
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

# Get unique supplier list
supplier_options = sorted(df_suppliers["Supplier Name"].unique().tolist())

# ── Criteria Definition ───────────────────────────────────────────────────────
criteria = [
    {"key": "preis", "label": "Preis", "weight": 0.30, "icon": "💶", "help": "How competitive and fair is the pricing?"},
    {"key": "trainer_expertise", "label": "Trainer Expertise", "weight": 0.25, "icon": "🧑‍🏫", "help": "How experienced and knowledgeable are the trainers?"},
    {"key": "industry_alignment", "label": "Industry Alignment", "weight": 0.20, "icon": "🏭", "help": "How well does the content align with industry needs?"},
    {"key": "training_duration", "label": "Training Duration", "weight": 0.15, "icon": "⏱️", "help": "Is the duration appropriate for the depth covered?"},
    {"key": "certification", "label": "Certification", "weight": 0.10, "icon": "🏅", "help": "How valuable and recognized is the certification?"},
]

# ── Main Evaluation Form ──────────────────────────────────────────────────────
with st.form("comparison_form"):
    st.subheader("🏢 Select 3 Suppliers to Compare")
    sel_col1, sel_col2, sel_col3 = st.columns(3)
    
    # Pre-populate index selections safely if there are enough unique suppliers
    with sel_col1:
        sup1 = st.selectbox("Supplier A", options=supplier_options, index=0)
    with sel_col2:
        sup2 = st.selectbox("Supplier B", options=supplier_options, index=min(1, len(supplier_options)-1))
    with sel_col3:
        sup3 = st.selectbox("Supplier C", options=supplier_options, index=min(2, len(supplier_options)-1))
        
    st.divider()
    st.subheader("📊 Performance

       
