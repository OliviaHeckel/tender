import streamlit as st
import os

# --- Page Configuration ---
st.set_page_config(page_title="RFQ Document Library", layout="wide")

# --- Absolute Paths ---
PDF_FOLDER = "maindoc.py/pages/newfolder"
THUMB_FOLDER = "maindoc.py/pages/my_new_folder"

st.title("📄 RFQ Document Library")
st.write("📅 Due date: 2026-06-25")

# --- Load PDF Files ---
if os.path.exists(PDF_FOLDER):
    pdf_files = sorted([f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")])
else:
    st.error(f"PDF folder not found at {PDF_FOLDER}")
    pdf_files = []


# --- Zoom Modal Function ---
@st.dialog("Document Preview", width="large")
def zoom_image(image_path, title):
    st.markdown(f"### {title}")
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.error("Image file not found.")
    
    if st.button("Close", use_container_width=True):
        st.rerun()


# --- Grid Configuration ---
NUM_COLUMNS = 3 

st.subheader("📁 Documents Gallery")

if pdf_files:
    # Chunk the pdf_files list into rows
    for i in range(0, len(pdf_files), NUM_COLUMNS):
        row_files = pdf_files[i : i + NUM_COLUMNS]
        cols = st.columns(NUM_COLUMNS)
        
        for idx, pdf in enumerate(row_files):
            with cols[idx]:
                base_name = os.path.splitext(pdf)[0]
                thumb_name = f"{base_name}.png"
                thumb_path = os.path.join(THUMB_FOLDER, thumb_name)
                pdf_path = os.path.join(PDF_FOLDER, pdf)

                with st.container(border=True):
                    # Display original small image in the grid
                    if os.path.exists(thumb_path):
                        st.image(thumb_path, use_container_width=True)
                    else:
                        st.warning(f"⚠️ '{thumb_name}' not found.")
                        
                    st.markdown(f"**{pdf}**")

                    # Action buttons beneath the image
                    btn_col1, btn_col2 = st.columns(2)
                    
                    with btn_col1:
                        # Triggers the overlay modal
                        if st.button("🔍 Zoom", key=f"z_{pdf}", use_container_width=True):
                            zoom_image(thumb_path, pdf)
            
                    with btn_col2:
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
else:
    st.info("No PDF files found to display.")
