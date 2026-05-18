import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Vertrag / Contract", layout="wide")

st.title("Vertrag / Contract")

# Updated date format to local style, though still a future date
st.write("📅 Fälligkeitsdatum / Due date: 2026-07-15")

# --- Document Upload Section ---
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

st.divider()

# --- Signature & Approval Tracker ---
st.subheader("✍️ Genehmigungsverfolgung / Approval Tracker")

# Replicate the logic from image_0.png where single people approve
# for multi-employee departments.
tracker_data = [
    # Department (Multi-line) from image | Approved?
    {"Abteilung": "Headquarters\nWeiterbildung", "Unterschrift": False},
    {"Abteilung": "Headquarters\nQualität", "Unterschrift": False},
    {"Abteilung": "Headquarters\nIndirekt Beschaffung", "Unterschrift": False},
    {"Abteilung": "Site (Hannover)\nQualität", "Unterschrift": False},
    {"Abteilung": "Site (Hannover)\nPersonalabteilung", "Unterschrift": False},
    {"Abteilung": "Kunde Account Manager\n(AUDI)", "Unterschrift": False}
]

# Ensure data is consistent even when new departments are added
if "approval_data_structured" not in st.session_state:
    st.session_state.approval_data_structured = tracker_data

# Function to update only the checkbox column
def update_signature_status(edited_data):
    current_data = st.session_state.approval_data_structured
    for idx, row in enumerate(edited_data):
        if idx < len(current_data):
            current_data[idx]["Unterschrift"] = row.get("Unterschrift", False)
    st.session_state.approval_data_structured = current_data

# Use a specific key for the interactive editor
if "edited_structured_data" not in st.session_state:
    st.session_state.edited_structured_data = []

# Display interactive data editor with text columns for Abteilung and checkbox for approval
edited_df = st.data_editor(
    st.session_state.approval_data_structured,
    column_config={
        "Abteilung": st.column_config.TextColumn(
            "Abteilung / Department",
            disabled=True,
            # Force the data_editor to honor multi-line text
            width="medium",
            help="Department information"
        ),
        "Unterschrift": st.column_config.CheckboxColumn(
            "Genehmigen / Approve", 
            default=False
        )
    },
    disabled=["Abteilung"], # Users can't edit the department names
    num_rows="fixed",       # Cannot add or delete rows
    hide_index=True,
    use_container_width=True,
    key="interactive_editor"
)

# Update the stored state (this runs on every interaction)
update_signature_status(edited_df)

# --- Progress Bar / Status ---
total_approvals = sum(1 for item in st.session_state.approval_data_structured if item.get("Unterschrift"))
total_required = len(st.session_state.approval_data_structured)

st.divider()

# Progress tracking
st.progress(total_approvals / total_required, text=f"Fortschritt / Progress: {total_approvals} von {total_required} Unterschriften gesammelt.")

if total_approvals == total_required:
    st.balloons()
    st.success("🎉 Alle Parteien haben den Vertrag genehmigt! / All parties have approved!")
elif total_approvals > 0:
    st.warning("⚠️ Unterschriften ausstehend. / Signatures outstanding.")

st.divider()

# --- Navigation ---
if st.button("⬅ Home"):
    # This assumes a main.py exists at the root
    try:
        st.switch_page("main.py")
    except Exception as e:
        st.error(f"Failed to navigate to main.py. Check your file structure. Error: {e}")
