import streamlit as st
import pandas as pd

st.set_page_config(page_title="Contract", layout="wide")

st.title("Contract")

st.write("📅 Due date: 2026-07-15")

# --- Document Upload Section ---
st.subheader("📁 Contract Document")
uploaded_file = st.file_uploader("Upload the contract document (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    # Optional: Add a button to preview or download the file
    st.download_button(
        label="Download Uploaded Contract",
        data=uploaded_file,
        file_name=uploaded_file.name,
        mime=uploaded_file.type
    )
else:
    st.info("Please upload a contract document to begin the approval process.")

st.divider()

# --- Signature & Approval Tracker ---
st.subheader("✍️ Signature & Approval Tracker")

# Initialize the tracking data in session state so changes persist
if "approval_data" not in st.session_state:
    # Default list of signees - you can modify this list as needed
    default_signees = {
        "Role": ["Legal Counsel", "Project Manager", "Finance Director", "Executive Sponsor"],
        "Name": ["Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince"],
        "Approved": [False, False, False, False]
    }
    st.session_state.approval_data = pd.DataFrame(default_signees)

# Display interactive data editor for users to check their approval
edited_df = st.data_editor(
    st.session_state.approval_data,
    column_config={
        "Role": st.column_config.TextColumn("Role", disabled=True),
        "Name": st.column_config.TextColumn("Name", disabled=True),
        "Approved": st.column_config.CheckboxColumn("Approve / Sign", default=False)
    },
    disabled=["Role", "Name"], # Only allow editing the 'Approved' checkbox
    hide_index=True,
    use_container_width=True
)

# Save changes back to session state
st.session_state.approval_data = edited_df

# --- Progress Bar / Status ---
total_approvals = edited_df["Approved"].sum()
total_required = len(edited_df)

st.write(f"**Progress:** {total_approvals} of {total_required} signatures collected.")
if total_approvals == total_required:
    st.balloons()
    st.success("🎉 All parties have approved the contract!")

st.divider()

# --- Navigation ---
if st.button("⬅ Home"):
    st.switch_page("main.py")
