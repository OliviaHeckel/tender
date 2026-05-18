import streamlit as st
import pandas as pd
import os
import sqlite3

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Team Supplier Evaluation",
    page_icon="👥",
    layout="wide",
)

# ── Database Initialization ──────────────────────────────────────────────────
# This database file sits on the server/host machine and is shared by all users
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

def save_rating(evaluator, supplier, score):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
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
st.title("👥 Team Supplier Evaluation & Alignment")
st.write("Collaborative scoring tool. Submit your individual scores below to update the team's average.")
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
    st.warning("⚠️ No filtered suppliers found. Please run the RFQ Generator first.")
    st.stop()

supplier_options = sorted(df_suppliers["Supplier Name"].unique().tolist())

# ── Criteria Definition ───────────────────────────────────────────────────────
criteria = [
    {"key": "preis", "label": "Preis", "weight": 0.30, "icon": "💶"},
    {"key": "trainer_expertise", "label": "Trainer Expertise", "weight": 0.25, "icon": "🧑‍🏫"},
    {"key": "industry_alignment", "label": "Industry Alignment", "weight": 0.20, "icon": "🏭"},
    {"key": "training_duration", "label": "Training Duration", "weight": 0.15, "icon": "⏱️"},
    {"key": "certification", "label": "Certification", "weight": 0.10, "icon": "🏅"},
]

# ── Step 1: User Identity & Supplier Selection ───────────────────────────────
st.subheader("✍️ Your Evaluation Session")
col_user, col_sup = st.columns(2)

with col_user:
    evaluator_name = st.text_input("Enter Your Name / Role:", placeholder="e.g., Procurement Manager, Tech Lead")
with col_sup:
    selected_supplier = st.selectbox("Select Supplier to Rate:", options=supplier_options)

st.divider()

# ── Step 2: Individual Evaluation Form ───────────────────────────────────────
if not evaluator_name.strip():
    st.info("💡 Please enter your name above to unlock the scoring matrix.")
else:
    with st.form("user_evaluation_form"):
        st.subheader(f"📋 Score Card for {selected_supplier} (Evaluating as: {evaluator_name})")
        
        user_scores = {}
        for c in criteria:
            weight_pct = f"{int(c['weight'] * 100)}%"
            user_scores[c["key"]] = st.slider(
                label=f"{c['icon']} {c['label']} (Weight: {weight_pct})",
                min_value=1,
                max_value=10,
                value=5,
                step=1,
                key=f"input_{c['key']}"
            )
            
        submit_rating = st.form_submit_button("Submit My Scores to Team Dashboard")

    if submit_rating:
        # Calculate individual weighted total
        individual_total = sum(user_scores[c["key"]] * c["weight"] for c in criteria)
        
        # Save securely to the shared database file
        save_rating(evaluator_name, selected_supplier, individual_total)
        st.success(f"✅ Thank you {evaluator_name}! Your score of **{individual_total:.2f}** for **{selected_supplier}** has been recorded.")

# ── Step 3: Global Team Summary Dashboard ─────────────────────────────────────
st.divider()
st.subheader("📊 Team Summary Dashboard")

# Read fresh data from the shared database file
df_global = load_all_ratings()

if df_global.empty:
    st.info("No evaluations have been submitted by the team yet. Be the first!")
else:
    # 1. Calculate Aggregated Averages per Supplier
    summary_df = df_global.groupby("supplier").agg(
        Average_Score=("final_score", "mean"),
        Total_Votes=("evaluator", "count")
    ).reset_index()
    
    # Sort by highest score
    summary_df = summary_df.sort_values(by="Average_Score", ascending=False).reset_index(drop=True)
    
    # 2. Display the current standing side-by-side
    st.write("### Current Standings (Aggregated Team Averages)")
    
    # Display top 3 metrics if available
    cols = st.columns(min(3, len(summary_df)))
    for index, row in summary_df.head(3).iterrows():
        if index < len(cols):
            cols[index].metric(
                label=f"Rank {index+1}: {row['supplier']}",
                value=f"{row['Average_Score']:.2f} / 10",
                delta=f"{row['Total_Votes']} reviews submitted"
            )
            
    # 3. Final Sourcing Award Statement
    st.divider()
    top_supplier = summary_df.iloc[0]["supplier"]
    top_score = summary_df.iloc[0]["Average_Score"]
    
    st.subheader("🏁 Current Sourcing Winner")
    st.success(f"🏆 **Based on all team inputs, the award goes to the one with the highest points: {top_supplier} ({top_score:.2f} / 10.00 average points)**")
    
    # 4. Show Raw History for complete audit transparency
    with st.expander("🔎 View detailed individual submission log"):
        st.dataframe(
            df_global[["evaluator", "supplier", "final_score"]].rename(
                columns={"evaluator": "Team Member", "supplier": "Supplier", "final_score": "Submitted Score"}
            ),
            use_container_width=True
        )

   
       
