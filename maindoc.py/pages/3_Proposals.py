import streamlit as st
import os


# --- Page Configuration ---
st.set_page_config(page_title="RFQ Document Library", layout="wide")

# --- Absolute Paths ---
# Verbatim paths as requested
PDF_FOLDER = "maindoc.py/pages/newfolder"
THUMB_FOLDER = "maindoc.py/pages/my_new_folder

st.title("📄 RFQ Document Library")
st.write("📅 Due date: 2026-06-25")

# --- Load PDF Files ---
if os.path.exists(PDF_FOLDER):
    # Get all PDFs from the rfq folder
    pdf_files = sorted([f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")])
else:
    st.error(f"PDF folder not found at {PDF_FOLDER}")
    pdf_files = []

# --- Session State ---
if "selected_item" not in st.session_state:
    st.session_state.selected_item = None

# --- Layout ---
col1, col2 = st.columns([1, 2])

# --- LEFT: Gallery (Using existing PNGs) ---
with col1:
    st.subheader("📁 Documents")
    
    for pdf in pdf_files:
        # Construct the expected PNG filename
        base_name = os.path.splitext(pdf)[0]
        thumb_name = f"{base_name}.png"
        thumb_path = os.path.join(THUMB_FOLDER, thumb_name)
        pdf_path = os.path.join(PDF_FOLDER, pdf)

        with st.container(border=True):
            # Direct display of existing PNG from thumbnails folder
            if os.path.exists(thumb_path):
                st.image(thumb_path, use_container_width=True)
            else:
                # If AutoTrain_RFQ.png isn't found, we show a warning[cite: 1]
                st.caption(f"⚠️ Thumbnail '{thumb_name}' not found in folder.")

            st.markdown(f"**{pdf}**")

            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                # Clicking View selects this file to show the picture on the right[cite: 1]
                if st.button("👁️ View", key=f"v_{pdf}", use_container_width=True):
                    st.session_state.selected_item = pdf
            
            with btn_col2:
                # Option to download the original PDF[cite: 1]
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 PDF",
                            data=f,
                            file_name=pdf,
                            mime="application/pdf",
                            key=f"d_{pdf}",
                            use_container_width=True
                        )

# --- RIGHT: Image Viewer ---
with col2:
    st.subheader("🖼️ Image Preview")
    
    if st.session_state.selected_item:
        selected_pdf = st.session_state.selected_item
        selected_thumb = f"{os.path.splitext(selected_pdf)[0]}.png"
        full_thumb_path = os.path.join(THUMB_FOLDER, selected_thumb)

        if os.path.exists(full_thumb_path):
            st.success(f"Displaying: {selected_thumb}")
            # Shows the picture from the thumbnails folder[cite: 1]
            st.image(full_thumb_path, use_container_width=True)
        else:
            st.error(f"Could not find '{selected_thumb}' in {THUMB_FOLDER}")
    else:
        st.info("Select a document's 'View' button to see the picture.")
