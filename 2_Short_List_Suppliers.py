
# Add the option that when I upload the PDF it converts to PNG and its availabe and view in the proposals page
#Currently is just a demo, cause I only have one auto generated example. 


import streamlit as st
import pandas as pd

df = pd.read_csv("main/filtered_supliers.csv")
if "Answer" not in df.columns:
    df["Answer"] = ""
    updated_rows = []

for i, row in df.iterrows():
    st.subheader(f"Supplier: {row['Supplier Name']}")  # change column name if needed
    
    answer = st.selectbox(
        "Answer",
        ["Yes", "No"],
        key=f"answer_{i}"
    )
    
    uploaded_file = st.file_uploader(
        "Upload document",
        key=f"file_{i}"
    )
    
    row["Answer"] = answer
    
    # Store file name (CSV can't store actual files)
    if uploaded_file:
        row["Document"] = uploaded_file.name
    else:
        row["Document"] = ""
    
    updated_rows.append(row)

updated_df = pd.DataFrame(updated_rows)

if st.button("Save"):
    updated_df.to_csv("updated_suppliers.csv", index=False)
    st.success("Saved successfully!")   



uploaded_file = st.file_uploader("Upload document")

if uploaded_file is not None:
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Saved file: {uploaded_file.name}")    
