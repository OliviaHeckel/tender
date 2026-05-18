import streamlit as st
import pandas as pd
import os

# 1. This must be called ONLY ONCE and at the very top of the script
st.set_page_config(page_title="Evaluation", layout="wide")

st.title("Evaluation")
st.write("📅 Due date: 2026-06-28")

# Configuration - CHECK THESE PATHS
SUPPLIER_FILE_PATH = "/Users/olivieol/Desktop/main/filtered_supliers.csv"
MATRIX_PATH = "training_evaluation_matrix.csv"

def load_data():
    suppliers = []
    criteria = []
    
    # 1. Load Suppliers
    if os.path.exists(SUPPLIER_FILE_PATH):
        try:
            sup_df = pd.read_csv(SUPPLIER_FILE_PATH)
            col_map = {c.lower(): c for c in sup_df.columns}
            if 'supplier name' in col_map:
                suppliers = sup_df[col_map['supplier name']].unique().tolist()
            elif 'supplier' in col_map:
                suppliers = sup_df[col_map['supplier']].unique().tolist()
            else:
                st.error(f"Found columns {sup_df.columns.tolist()}, but none match 'supplier name'.")
        except Exception as e:
            st.error(f"Error reading Suppliers: {e}")
    else:
        st.error(f"File NOT found: {SUPPLIER_FILE_PATH}. Check the path/spelling.")

    # 2. Load Matrix Criteria
    if os.path.exists(MATRIX_PATH):
        try:
            matrix_df = pd.read_csv(MATRIX_PATH)
            criteria = [col for col in matrix_df.columns if '(' in col and '%' in col]
        except Exception as e:
            st.error(f"Error reading Matrix: {e}")
    else:
        st.error(f"File NOT found: {MATRIX_PATH}")

    return suppliers, criteria


def main():
    # Removed st.set_page_config from here
    st.header("🏆 Final Award Selection")

    suppliers, criteria = load_data()
    if not suppliers or not criteria:
        st.stop()

    all_final_scores = []

    with st.form("evaluation_form"):
        for supplier in suppliers:
            with st.expander(f"Assess: {supplier}", expanded=False):
                cols = st.columns(len(criteria))
                total_weighted = 0.0
                for i, crit in enumerate(criteria):
                    weight_val = float(crit.split('(')[-1].split('%')[0]) / 100
                    score = cols[i].select_slider(f"{crit}", options=[1,2,3,4,5], value=3, key=f"{supplier}_{crit}")
                    total_weighted += (score * weight_val)
                
                all_final_scores.append({"Supplier": supplier, "Final Score": round(total_weighted, 2)})

        submit = st.form_submit_button("Generate Award File")

    if submit:
        res_df = pd.DataFrame(all_final_scores).sort_values(by="Final Score", ascending=False)
        
        # Show Results UI
        st.divider()
        st.dataframe(res_df, use_container_width=True)
        st.bar_chart(res_df.set_index("Supplier"))
        
        # Winner Logic
        winner_name = res_df.iloc[0]['Supplier']
        winner_score = res_df.iloc[0]['Final Score']

        # File creation logic
        clean_name = "".join([c for c in winner_name if c.isalnum() or c in (' ', '_')]).strip()
        filename = f"{clean_name}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"AWARD WINNER: {winner_name}\nSCORE: {winner_score}")

        st.balloons()
        st.success(f"Award file created for {winner_name}!")

if __name__ == "__main__":
    main()
