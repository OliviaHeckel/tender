import streamlit as st
import pandas as pd
import os
import sqlite3

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Team Supplier Evaluation Matrix & Contract Tracker",
    page_icon="👥",
    layout="wide",
)

# ── Hide Developer UI & Source Code Options ──────────────────────────────────
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
st.title("🎯 Collaborative Supplier Evaluation & Contract Tracking Hub")
st.write("Select your organizational role, manage structural contract approvals, and evaluate suppliers simultaneously.")
st.divider()

# --- Section 1: Document Upload & Approval Tracker ---
st.header("📄 Contract Management")

st.subheader("📁 Vertragsunterlage / Contract Document")
uploaded_file = st.file_uploader("Vertrag hochladen / Upload the contract (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    st.success(f"Datei '{uploaded_file.name}' erfolgreich hochgeladen / uploaded successfully!")
    st.download_button(
        label="Vertrag herunterladen / Download Contract",
        data=uploaded_file,
        file_name=uploaded_file.name,
        mime=uploaded_file.type
    )
else:
    st.info("Bitte hochladen / Please upload to begin the approval process.")

st.subheader("✍️ Genehmigungsverfolgung / Approval Tracker")

tracker_data = [
    {"Abteilung": "Headquarters\nWeiterbildung", "Unterschrift": False},
    {"Abteilung": "Headquarters\nQualität", "Unterschrift": False},
    {"Abteilung": "Headquarters\nIndirekt Beschaffung", "Unterschrift": False},
    {"Abteilung": "Site (Hannover)\nQualität", "Unterschrift": False},
    {"Abteilung": "Site (Hannover)\nPersonalabteilung", "Unterschrift": False},
    {"Abteilung": "Kunde Account Manager\n(AUDI)", "Unterschrift": False}
]

if "approval_data_structured" not in st.session_state:
    st.session_state.approval_data_structured = tracker_data

def update_signature_status(edited_data):
    current_data = st.session_state.approval_data_structured
    for idx, row in enumerate(edited_data):
        if idx < len(current_data):
            current_data[idx]["Unterschrift"] = row.get("Unterschrift", False)
    st.session_state.approval_data_structured = current_data

edited_df = st.data_editor(
    st.session_state.approval_data_structured,
    column_config={
        "Abteilung": st.column_config.TextColumn(
            "Abteilung / Department",
            disabled=True,
            width="medium",
            help="Department information"
        ),
        "Unterschrift": st.column_config.CheckboxColumn(
            "Genehmigen / Approve", 
            default=False
        )
    },
    disabled=["Abteilung"],
    num_rows="fixed",
    hide_index=True,
    use_container_width=True,
    key="interactive_editor"
)

update_signature_status(edited_df)

total_approvals = sum(1 for item in st.session_state.approval_data_structured if item.get("Unterschrift"))
total_required = len(st.session_state.approval_data_structured)

st.progress(total_approvals / total_required, text=f"Fortschritt / Progress: {total_approvals} von {total_required} Unterschriften gesammelt.")

if total_approvals == total_required:
    st.balloons()
    st.success("🎉 Alle Parteien haben den Vertrag genehmigt! / All parties have approved!")
elif total_approvals > 0:
    st.warning("⚠️ Unterschriften ausstehend. / Signatures outstanding.")

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
