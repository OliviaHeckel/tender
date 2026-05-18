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
    st.subheader("📊 Performance Matrix Evaluation (Rate 1 - 10)")
    
    # Dictionary to hold input scores
    scores = {sup1: {}, sup2: {}, sup3: {}}
    
    # Loop through criteria to render input sliders in columns side-by-side
    for c in criteria:
        st.write(f"### {c['icon']} {c['label']} (Weight: {int(c['weight'] * 100)}%)")
        st.caption(c['help'])
        
        c_col1, c_col2, c_col3 = st.columns(3)
        
        with c_col1:
            scores[sup1][c['key']] = st.slider(f"Score for {sup1}", min_value=1, max_value=10, value=5, step=1, key=f"s1_{c['key']}")
        with c_col2:
            scores[sup2][c['key']] = st.slider(f"Score for {sup2}", min_value=1, max_value=10, value=5, step=1, key=f"s2_{c['key']}")
        with c_col3:
            scores[sup3][c['key']] = st.slider(f"Score for {sup3}", min_value=1, max_value=10, value=5, step=1, key=f"s3_{c['key']}")
            
        st.divider()
        
    submit_comparison = st.form_submit_button("Calculate Results & Compare Matrix")

# ── Evaluation Results and Sourcing Decision ─────────────────────────────────
if submit_comparison:
    # Compute weighted scores
    totals = {}
    for supplier in [sup1, sup2, sup3]:
        totals[supplier] = sum(scores[supplier][c['key']] * c['weight'] for c in criteria)
        
    st.subheader("📊 Evaluation Comparison Summary")
    
    # Display the final performance metrics side-by-side
    res_col1, res_col2, res_col3 = st.columns(3)
    with res_col1:
        st.metric(label=f"🏆 {sup1} Total Score", value=f"{totals[sup1]:.2f} / 10.00")
    with res_col2:
        st.metric(label=f"🏆 {sup2} Total Score", value=f"{totals[sup2]:.2f} / 10.00")
    with res_col3:
        st.metric(label=f"🏆 {sup3} Total Score", value=f"{totals[sup3]:.2f} / 10.00")
        
    st.divider()
    
    # Generate structured analysis table for visual breakdown
    st.write("### Detailed Score Comparison Table")
    comparison_data = []
    for c in criteria:
        comparison_data.append({
            "Criterion": f"{c['icon']} {c['label']}",
            "Weight": f"{int(c['weight'] * 100)}%",
            f"{sup1} (Raw / Weighted)": f"{scores[sup1][c['key']]} / {(scores[sup1][c['key']]*c['weight']):.2f}",
            f"{sup2} (Raw / Weighted)": f"{scores[sup2][c['key']]} / {(scores[sup2][c['key']]*c['weight']):.2f}",
            f"{sup3} (Raw / Weighted)": f"{scores[sup3][c['key']]} / {(scores[sup3][c['key']]*c['weight']):.2f}",
        })
    st.table(pd.DataFrame(comparison_data))
    
    st.divider()
    
    # Determine winner based on maximum points
    winner = max(totals, key=totals.get)
    highest_score = totals[winner]
    
    # Strict award decision output block
    st.subheader("🏁 Sourcing Decision")
    st.success(f"🏆 **The award goes to the one with the highest point: {winner} ({highest_score:.2f} / 10.00 points)**")
