import streamlit as st
import pandas as pd
import os
import sqlite3


# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎯 Collaborative Supplier Evaluation & Contract Tracking Hub")
st.write("Select your organizational role, manage structural contract approvals, and evaluate suppliers simultaneously.")
st.divider()




# ── Section 2: Load Filtered Suppliers ────────────────────────────────────────
csv_path = "filtered_supliers.csv"

if os.path.exists(csv_path):
    try:
        df_suppliers = pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        df_suppliers = pd.DataFrame()
else:
    df_suppliers = pd.DataFrame()

if df_suppliers.empty:
    st.warning("⚠️ No filtered suppliers found. Please run the RFQ Generator first to generate `filtered_supliers.csv`.")
    st.stop()

supplier_options = sorted(df_suppliers["Supplier Name"].unique().tolist())

# ── Criteria Definition ───────────────────────────────────────────────────────
criteria = [
    {"key": "preis", "label": "Preis", "weight": 0.30, "icon": "💶", "help": "How competitive and fair is the pricing?"},
    {"key": "trainer_expertise", "label": "Trainer Expertise", "weight": 0.25, "icon": "🧑‍🏫", "help": "How experienced and knowledgeable are the trainers?"},
    {"key": "industry_alignment", "label": "Industry Alignment", "weight": 0.20, "icon": "🏭", "help": "How well does the content align with industry needs?"},
    {"key": "training_duration", "label": "Training Duration", "weight": 0.15, "icon": "⏱️", "help": "Is the duration appropriate for the depth covered?"},
    {"key": "certification", "label": "Certification", "weight": 0.10, "icon": "🏅", "help": "How valuable and recognized is the certification?"},
]

# ── Step 1: Evaluator Info (With new Position Dropdown) & Supplier Setup ──────
st.header("⚖️ Supplier Evaluation Matrix")
st.subheader("✍️ Evaluation Session Setup")
col_user, col_pos, col_s1, col_s2, col_s3 = st.columns(5)

with col_user:
    evaluator_name = st.text_input("Your Name:", placeholder="e.g., Jane Doe")

with col_pos:
    # Extracted positions dropdown compiled directly from the structural matrix categories
    position_options = [
        "Headquarters Weiterbildung",
        "Headquarters Qualität",
        "Headquarters Indirekt Beschaffung",
        "Site (Hannover) Qualität",
        "Site (Hannover) Personalabteilung",
        "Kunde Account Manager (AUDI)"
    ]
    selected_position = st.selectbox("Your Position / Department:", options=position_options)

with col_s1:
    sup1 = st.selectbox("Supplier A", options=supplier_options, index=0)
with col_s2:
    sup2 = st.selectbox("Supplier B", options=supplier_options, index=min(1, len(supplier_options)-1))
with col_s3:
    sup3 = st.selectbox("Supplier C", options=supplier_options, index=min(2, len(supplier_options)-1))

# Combine Name and Position for database logging context
full_evaluator_identity = f"{evaluator_name} ({selected_position})" if evaluator_name.strip() else ""

st.divider()

# ── Step 2: Simultaneous Evaluation Form ──────────────────────────────────────
if not evaluator_name.strip():
    st.info("💡 Please enter your name above to unlock the scoring matrix for the selected suppliers.")
else:
    with st.form("simultaneous_matrix_form"):
        st.subheader(f"📋 Simultaneous Matrix (Evaluating as: {full_evaluator_identity})")
        
        session_scores = {sup1: {}, sup2: {}, sup3: {}}
        
        for c in criteria:
            st.write(f"### {c['icon']} {c['label']} (Weight: {int(c['weight'] * 100)}%)")
            st.caption(c['help'])
            
            c_col1, c_col2, c_col3 = st.columns(3)
            with c_col1:
                session_scores[sup1][c['key']] = st.slider(f"Score for {sup1}", min_value=1, max_value=10, value=5, step=1, key=f"s1_{c['key']}")
            with c_col2:
                session_scores[sup2][c['key']] = st.slider(f"Score for {sup2}", min_value=1, max_value=10, value=5, step=1, key=f"s2_{c['key']}")
            with c_col3:
                session_scores[sup3][c['key']] = st.slider(f"Score for {sup3}", min_value=1, max_value=10, value=5, step=1, key=f"s3_{c['key']}")
            st.divider()
            
        submit_matrix = st.form_submit_button(f"Submit All 3 Evaluations as {full_evaluator_identity}")

    if submit_matrix:
        calculated_totals = {}
        for supplier in [sup1, sup2, sup3]:
            calculated_totals[supplier] = sum(session_scores[supplier][c['key']] * c['weight'] for c in criteria)
            
        # Saves evaluation under the pattern: "Name (Position)"
        save_multiple_ratings(full_evaluator_identity, calculated_totals)
        st.success(f"✅ Matrix submission complete! Evaluated {sup1}, {sup2}, and {sup3} successfully.")

# ── Step 3: Consolidated Team Summary Dashboard ───────────────────────────────
st.subheader("📊 Consolidated Team Summary Dashboard")
df_global = load_all_ratings()

if df_global.empty:
    st.info("No evaluations have been logged by the team yet. Complete your session setup above to record the first matrix entry.")
else:
    summary_df = df_global.groupby("supplier").agg(
        Average_Score=("final_score", "mean"),
        Total_Reviews=("evaluator", "count")
    ).reset_index()
    
    summary_df = summary_df.sort_values(by="Average_Score", ascending=False).reset_index(drop=True)
    
    st.write("### Current Standings (Aggregated Team Averages)")
    
    cols = st.columns(min(3, len(summary_df)))
    for index, row in summary_df.head(3).iterrows():
        if index < len(cols):
            cols[index].metric(
                label=f"Rank {index+1}: {row['supplier']}",
                value=f"{row['Average_Score']:.2f} / 10",
                delta=f"{row['Total_Reviews']} submissions logged"
            )
            
    st.divider()
    
    top_supplier = summary_df.iloc[0]["supplier"]
    top_score = summary_df.iloc[0]["Average_Score"]
    
    st.subheader("🏁 Sourcing Decision Award")
    st.success(f"🏆 **Based on all compiled entries, the award goes to: {top_supplier} ({top_score:.2f} / 10.00 average points)**")
    
    with st.expander("🔎 View detailed individual submission log"):
        st.dataframe(
            df_global[["evaluator", "supplier", "final_score"]].rename(
                columns={"evaluator": "Team Member (Position)", "supplier": "Supplier", "final_score": "Total Score Result"}
            ),
            use_container_width=True
        )

st.divider()

# ── Navigation ────────────────────────────────────────────────────────────────
if st.button("⬅ Home"):
    try:
        st.switch_page("main.py")
    except Exception as e:
        st.error(f"Failed to navigate to main.py. Check your file structure. Error: {e}")
