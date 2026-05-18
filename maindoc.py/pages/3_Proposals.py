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

# --- Grid Configuration ---
# Choose how many columns you want in your grid (e.g., 3 or 4 looks great on 'wide' layout)
NUM_COLUMNS = 3 

st.subheader("📁 Documents Gallery")

if pdf_files:
    # Chunk the pdf_files list into rows of size NUM_COLUMNS
    for i in range(0, len(pdf_files), NUM_COLUMNS):
        row_files = pdf_files[i : i + NUM_COLUMNS]
        
        # Create the columns for this specific row
        cols = st.columns(NUM_COLUMNS)
        
        for idx, pdf in enumerate(row_files):
            with cols[idx]:
                # Construct paths
                base_name = os.path.splitext(pdf)[0]
                thumb_name = f"{base_name}.png"
                thumb_path = os.path.join(THUMB_FOLDER, thumb_name)
                pdf_path = os.path.join(PDF_FOLDER, pdf)

                # Wrap each card in a clean border box
                with st.container(border=True):
                    # Direct display of existing PNG
                    if os.path.exists(thumb_path):
                        st.image(thumb_path, use_container_width=True)
                    else:
                        # Fallback placeholder if image doesn't exist
                        st.warning(f"⚠️ '{thumb_name}' not found.")
                        
                    st.markdown(f"**{pdf}**")

                    # Download button directly below the image
                    if os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="📥 Download PDF",
                                data=f,
                                file_name=pdf,
                                mime="application/pdf",
                                key=f"d_{pdf}",
                                use_container_width=True
                            )
else:
    st.info("No PDF files found to display.")
