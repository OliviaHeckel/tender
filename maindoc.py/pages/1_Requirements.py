import streamlit as st
import pandas as pd



# 1. Setup and Data Loading
st.set_page_config(page_title="RFQ Generator", layout="wide")
df = pd.read_csv("automotive_training_suppliers_europe.csv")

# Helper to check ranges like "12-20"
def check_capacity(range_str, required):
    try:
        parts = [p.strip() for p in str(range_str).split("-") if p.strip()]
        if len(parts) == 2:
            min_p, max_p = int(parts[0]), int(parts[1])
            if min_p <= required <= max_p:
                return True, "OK"
            return False, "check participants range"
    except:
        pass
    return True, "OK"

# Initialize session state for custom suppliers
if "custom_suppliers" not in st.session_state:
    st.session_state.custom_suppliers = []

st.title("Supplier Selection & RFQ Generator")

# 2. Main Input Form
with st.form("main_form"):
    st.subheader("📋 Training Requirements")
    col1, col2 = st.columns(2)
    
    with col1:
        # Extract training types from CSV [cite: 1]
        all_types = sorted(list(set([t.strip() for val in df["Training Types Offered"] for t in str(val).split(";") if t.strip()])))
        selected_training = st.selectbox("Training Type", options=all_types)
        participants = st.number_input("Amount of Participants", min_value=1, value=15)
        
    with col2:
        delivery = st.selectbox("Delivery Mode", ["On-site", "Virtual", "Hybrid", "Classroom", "Lab-based"])
        language = st.selectbox("Language", ["English", "German", "French", "Italian", "Spanish"])

    st.subheader("📅 Proposed Time Slots (Select at least 2)")
    d_col1, d_col2 = st.columns(2)
    slot1 = d_col1.date_input("Slot 1")
    slot2 = d_col2.date_input("Slot 2")

    submit_find = st.form_submit_button("Find Suppliers & Generate RFQ")

# 3. Add Custom Suppliers (Outside the main form to avoid nesting)
with st.expander("➕ Add your own supplier to this list"):
    with st.container():
        c_name = st.text_input("Supplier Name")
        c_email = st.text_input("Contact Email")
        if st.button("Add Supplier"):
            if c_name and c_email:
                st.session_state.custom_suppliers.append({"Supplier Name": c_name, "Contact Email": c_email})
                st.success(f"Added {c_name}!")

# 4. Logic execution after clicking "Find"
if submit_find:
    # Filter logic [cite: 1]
    matches = df[
        (df["Training Types Offered"].str.contains(selected_training, case=False)) &
        (df["Delivery Mode"].str.contains(delivery, case=False)) &
        (df["Languages Available"].str.contains(language, case=False))
    ].copy()

    st.divider()
    st.subheader("🔎 Supplier Recommendation Results")

    valid_emails = []

    if matches.empty and not st.session_state.custom_suppliers:
        st.warning("No suppliers found matching those criteria.")
    else:
        # Save filtered suppliers to a CSV document and provide download
        try:
            out_path = "./filtered_supliers.csv"
            matches.to_csv(out_path, index=False)
            st.success(f"Filtered suppliers saved to `{out_path}`")
        except Exception as e:
            st.error(f"Could not save filtered suppliers file: {e}")

        csv_data = matches.to_csv(index=False)
        st.download_button(
            label="📥 Download filtered suppliers CSV",
            data=csv_data,
            file_name="filtered_supliers.csv",
            mime="text/csv",
        )

        # Display CSV Matches
        for _, row in matches.iterrows():
            is_valid, msg = check_capacity(row["Participants per Session"], participants)
            
            with st.container():
                st.write(f"### {row['Supplier Name']}")
                if not is_valid:
                    st.error(f"❌ {msg} (Supplier limit: {row['Participants per Session']})")
                else:
                    st.success(f"✅ Capacity OK ({row['Participants per Session']})")
                    valid_emails.append(row["Contact Email"])
                st.write(f"**Contact:** {row['Contact Email']}")
                st.divider()

        # Display Custom Suppliers
        for cust in st.session_state.custom_suppliers:
            st.info(f"📌 Custom Supplier: {cust['Supplier Name']} ({cust['Contact Email']})")
            valid_emails.append(cust["Contact Email"])

        # 5. THE EMAIL TEXT DOCUMENT (Visible Result)
        if valid_emails:
            st.subheader("📧 Generated RFQ Email Content")
            st.write("Copy the text below to send to your selected suppliers:")
            
            email_body = f"""
To: {", ".join(valid_emails)}
Subject: Request for Quotation: {selected_training} Training

Dear Training Providers,

We are seeking a quotation for the following training requirement:

- Training: {selected_training}
- Participants: {participants}
- Delivery Mode: {delivery}
- Language: {language}

We would like to propose the following time slots for this session:
1. {slot1}
2. {slot2}

Please provide your best offer and confirm which of these dates would work for your trainers.

Best regards,
[Your Name/Company]
            """
            
            # Using st.text_area so the user can easily copy the text
            st.text_area(label="RFQ Text Document", value=email_body, height=350)
            
            # Optional: A button to download it as a .txt file
            st.download_button(
                label="📥 Download RFQ as Text File",
                data=email_body,
                file_name="RFQ_Request.txt",
                mime="text/plain")   









