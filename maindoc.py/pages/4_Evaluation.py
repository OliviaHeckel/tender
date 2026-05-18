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
    sup2 = st.selectbox("Supplier B", options=supplier_options,

