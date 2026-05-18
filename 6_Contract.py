import streamlit as st

st.set_page_config(page_title="Contract", layout="wide")

st.title("Contract")

st.write("📅 Due date: 2026-07-15")

if st.button("⬅ Home"):
    st.switch_page("main.py")
