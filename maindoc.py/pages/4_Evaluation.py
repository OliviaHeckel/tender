import streamlit as st
import pandas as pd
import os
import sqlite3

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Team Supplier Evaluation Matrix",
    page_icon="👥",
    layout="wide",
)

# ── Hide Developer UI & Source Code Options ──────────────────────────────────
# This completely removes the MainMenu, header toolbar, and footer for the end-user
hide_ui_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_ui_style, unsafe_allow_html=True)

# ── Database Initialization ──────────────────────────────────────────────────
DB_FILE = "team_evaluations.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluator TEXT,
            supplier TEXT,
            final_score REAL
        )
    """)
    conn.commit()
    conn.close()

def save_multiple_ratings(evaluator, supplier_scores):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for supplier, score in supplier_scores.items():
        c.execute("INSERT INTO ratings (evaluator, supplier, final_score) VALUES (?, ?, ?)", 
                  (evaluator, supplier, score))
    conn.commit()
    conn.close()

def load_all_ratings():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM ratings", conn)
    conn.close()
    return df

# Initialize the shared database
init_db()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎯 Collaborative Supplier Evaluation Matrix")
st.write("Enter your role, select three suppliers, and evaluate them simultaneously. Your entries will be aggregated into the team's final decision.")
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

# ── Step 1: Evaluator Info & Supplier Setup ──────────────────────────────────
st.subheader("✍️ Evaluation Session Setup")
col_user, col_s1, col_s2, col_s3 = st.columns(4)

with col_user:
    evaluator_name = st.text_input("Your Name / Role:", placeholder="e.g., Quality Auditor, Tech Lead")
with col_s1:
    sup1 = st.selectbox("Supplier A", options=supplier_options, index=0)
with col_s2:
    sup2 = st.selectbox("Supplier B", options=supplier_options, index=min(1, len(supplier_options)-1))
with col_s3:
    sup3 = st.selectbox("Supplier C", options=supplier_options, index=min(2, len(supplier_options)-1))

st.divider()

# ── Step 2: Simultaneous Evaluation Form ──────────────────────────────────────
if not evaluator_name.strip():
    st.info("💡 Please enter your name/role above to unlock the scoring matrix for the selected suppliers.")
else:
    with st.form("simultaneous_matrix_form"):
        st.subheader(f"📋 Simultaneous Matrix (Evaluating as: {evaluator_name})")
        
        # Nested structure to hold scores: scores[supplier][criterion_key]
        session_scores = {sup1: {}, sup2: {}, sup3: {}}
        
        # Generate side-by-side sliders per criterion
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
            
        submit_matrix = st.form_submit_button(f"Submit All 3 Evaluations as {evaluator_name}")

    if submit_matrix:
        # Calculate individual weighted totals for this submission
        calculated_totals = {}
        for supplier in [sup1, sup2, sup3]:
            calculated_totals[supplier] = sum(session_scores[supplier][c['key']] * c['weight'] for c in criteria)
            
        # Write all 3 evaluations to the persistent database file simultaneously
        save_multiple_ratings(evaluator_name, calculated_totals)
        st.success(f"✅ Matrix submission complete! Evaluated {sup1}, {sup2}, and {sup3} successfully.")

# ── Step 3: Consolidated Team Summary Dashboard ───────────────────────────────
st.subheader("📊 Consolidated Team Summary Dashboard")
df_global = load_all_ratings()

if df_global.empty:
    st.info("No evaluations have been logged by the team yet. Complete your session setup above to record the first matrix entry.")
else:
    # Group, aggregate, and average ratings from all team members across all sessions
    summary_df = df_global.groupby("supplier").agg(
        Average_Score=("final_score", "mean"),
        Total_Reviews=("evaluator", "count")
    ).reset_index()
    
    # Sort descending by performance score
    summary_df = summary_df.sort_values(by="Average_Score", ascending=False).reset_index(drop=True)
    
    st.write("### Current Standings (Aggregated Team Averages)")
    
    # Render top performance metrics side-by-side using native metrics
    cols = st.columns(min(3, len(summary_df)))
    for index, row in summary_df.head(3).iterrows():
        if index < len(cols):
            cols[index].metric(
                label=f"Rank {index+1}: {row['supplier']}",
                value=f"{row['Average_Score']:.2f} / 10",
                delta=f"{row['Total_Reviews']} submissions logged"
            )
            
    st.divider()
    
    # Top supplier extraction
    top_supplier = summary_df.iloc[0]["supplier"]
    top_score = summary_df.iloc[0]["Average_Score"]
    
    # Target decision award statement execution
    st.subheader("🏁 Sourcing Decision Award")
    st.success(f"🏆 **Based on all compiled entries, the award goes to the one with the highest points: {top_supplier} ({top_score:.2f} / 10.00 average points)**")
    
    # Full history expansion for evaluation audits
    with st.expander("🔎 View detailed individual submission log"):
        st.dataframe(
            df_global[["evaluator", "supplier", "final_score"]].rename(
                columns={"evaluator": "Team Member/Role", "supplier": "Supplier", "final_score": "Total Score Result"}
            ),
            use_container_width=True
        )
