import streamlit as st
import pandas as pd
import re
import datetime
from io import BytesIO

# --- UI CONFIG ---
st.set_page_config(page_title="Aiolos Excel Classifier", layout="centered")
st.markdown("""
    <style>
        body {
            font-family: 'Helvetica Neue', sans-serif;
        }
        .stApp {
            background-color: #f7f9fc;
        }
        .title {
            color: #003366;
            font-size: 2.5em;
            font-weight: 600;
            margin-bottom: 0.2em;
        }
        .subtitle {
            color: #4a6fa5;
            font-size: 1.1em;
            margin-bottom: 2em;
        }
        .css-1emrehy.edgvbvh3, .stButton>button {
            background-color: #003366;
            color: white;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #004080;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<div class='title'>Aiolos</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Excel Classification Tool</div>", unsafe_allow_html=True)

# --- PROJECT SELECTION ---
project_type = st.selectbox("Choose Excel Format:", ["DIAKOFTI"], index=0)

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "csv"])

# --- PLOT RECOGNITION ---
PLOTS = [
    'Y1', 'Y2', 'Y3', 'Y6', 'Y4-7', 'Y8', 'R2', 'R4', 'B5', 'G2',
    'R5A', 'R5B', 'R5C', 'R5D', 'W2', 'W8', 'B6', 'G1', 'G12', 'G13', 'B9-10-11'
]

def find_all_plots(description):
    found = []
    for plot in PLOTS:
        if re.search(rf"(?<!\w){re.escape(plot)}(?!\w)", description):
            found.append(plot)
    return found

# --- MAIN PROCESSING FUNCTION ---
def process_file(df):
    df = df.dropna(subset=['ΠΕΡΙΓΡΑΦΗ'])
    df['ΠΟΣΟ'] = df['ΠΟΣΟ'].astype(str).str.replace('.', '').str.replace(',', '.').astype(float)

    results = []
    for _, row in df.iterrows():
        desc = str(row['ΠΕΡΙΓΡΑΦΗ']).upper()
        amount = abs(row['ΠΟΣΟ'])
        plots = find_all_plots(desc)

        if len(plots) == 1:
            plot_val = plots[0]
        elif len(plots) > 1:
            plot_val = "Multiple"
        else:
            plot_val = "All Plots"

        is_income = row['ΠΟΣΟ'] > 0

        entry = {
            "Date": row['ΗΜ/ΝΙΑ ΚΙΝΗΣΗΣ'],
            "Income/outcome": "Income" if is_income else "Outcome",
            "Plot": plot_val,
            "Expenses Type": "Soft Cost",
            "Type": "",
            "Supplier": "",
            "Description": desc,
            "In": amount if is_income else "",
            "Out": -amount if not is_income else "",
            "Total": amount if is_income else -amount,
            "Progressive Ledger Balance": "",
            "Payment details": ""
        }

        # --- Custom Rules ---
        if "COM POO" in desc:
            entry["Type"] = "Bank"
            entry["Supplier"] = "Bank"
        if any(term in desc for term in ["ACCOUNTING", "BOOKKEEP", "ECOVIS"]) and not any(word in desc for word in ["YAG", "TAG"]):
            entry["Type"] = "Accounting"
            entry["Supplier"] = "Ecovis"
        if "GAS" in desc:
            entry["Type"] = "Fuel"
            entry["Supplier"] = "Gas Station"
        if "DRAKAKIS" in desc:
            entry["Type"] = "Project management"
            entry["Supplier"] = "Drakakis Tours"
        if "COSM" in desc or "PHONE" in desc:
            entry["Type"] = "Utility Bills"
            entry["Supplier"] = "Cosmote"
        if "GOOGLE" in desc:
            entry["Type"] = "Marketing"
            entry["Supplier"] = "Google"
        if "UBER" in desc:
            entry["Type"] = "Transportation"
            entry["Supplier"] = "Uber"
        if "AEGEAN" in desc:
            entry["Type"] = "Travel"
            entry["Supplier"] = "Aegean"
        if "OPENAI" in desc:
            entry["Type"] = "SaaS"
            entry["Supplier"] = "OpenAI"
        if any(word in desc for word in ["DINNER", "FOOD", "CAFE", "COFFEE", "LUNCH", "BREAKFAST"]):
            entry["Type"] = "General"
            entry["Supplier"] = "F&B"
        if "CAR" in desc:
            entry["Type"] = "Transportation"
            entry["Supplier"] = "Car Rental"
        if "OASA" in desc:
            entry["Type"] = "Transportation"
            entry["Supplier"] = "OASA (Metro)"
        if "CALEN" in desc:
            entry["Type"] = "Construction works"
            entry["Supplier"] = "Calen"
            entry["Expenses Type"] = "Hard Cost"
        if "CRM" in desc:
            entry["Type"] = "reWire"
            entry["Supplier"] = "Marketing"
            entry["Description"] = "CRM"
            entry["Expenses Type"] = "Soft Cost"

        if "CONSTRUCTION" in desc or "HARD COST" in desc:
            entry["Expenses Type"] = "Hard Cost"

        results.append(entry)

    return pd.DataFrame(results)

# --- RUN ---
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        raw_df = pd.read_csv(uploaded_file, encoding="ISO-8859-7")
    else:
        raw_df = pd.read_excel(uploaded_file)

    result_df = process_file(raw_df)

    st.success("✅ File processed successfully!")
    st.dataframe(result_df.head(50))

    to_download = BytesIO()
    result_df.to_excel(to_download, index=False, engine='openpyxl')
    st.download_button(
        label="Download Processed File",
        data=to_download.getvalue(),
        file_name=f"aiolos_processed_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
