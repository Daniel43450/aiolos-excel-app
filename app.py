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
        .decor-box {
            background-color: #e6f0ff;
            border-left: 6px solid #003366;
            padding: 1em;
            margin: 2em auto;
            width: 90%;
            border-radius: 8px;
            font-size: 1em;
            color: #003366;
        }
        .stButton>button {
            background-color: #003366;
            color: white;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #004080;
            color: white;
        }
        .logo {
            display: flex;
            justify-content: center;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .logo img {
            width: 120px;
            border-radius: 100px;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGO ---
st.markdown("""
    <div class='logo'>
        <img src='https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG' alt='Aiolos Logo'>
    </div>
""", unsafe_allow_html=True)

# --- Decorative Section ---
st.markdown("""
    <div class='decor-box'>
        Upload your financial Excel statement and get an automatically categorized version ready for download — powered by Aiolos.
    </div>
""", unsafe_allow_html=True)

# --- PROJECT SELECTION ---
project_type = st.selectbox("Choose Excel Format:", ["DIAKOFTI", "ATHENS"], index=0)

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
        if re.search(rf"(?<!\\w){re.escape(plot)}(?!\\w)", description):
            found.append(plot)
    return found

# Placeholder for ATHENS processing (to be implemented later)
def process_athens_file(df):
    df["NOTE"] = "ATHENS format not yet supported"
    return df

# --- MAIN PROCESSING FUNCTION FOR DIAKOFTI ---
def process_file(df):
    df = df.dropna(subset=['ΠΕΡΙΓΡΑΦΗ'])
    df['ΠΟΣΟ'] = df['ΠΟΣΟ'].astype(str).str.replace('.', '').str.replace(',', '.').astype(float)

    results = []
    for _, row in df.iterrows():
        original_desc = str(row['ΠΕΡΙΓΡΑΦΗ'])
        desc = original_desc.upper()
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
            "Payment details": "",
            "Original Description": original_desc
        }

        filled = False

        if "COM POO" in desc:
            entry["Type"] = "Bank"
            entry["Supplier"] = "Bank"
            entry["Description"] = "Bank fees"
            filled = True
        if any(term in desc for term in ["ACCOUNTING", "BOOKKEEP", "ECOVIS"]) and not any(word in desc for word in ["YAG", "TAG"]):
            entry["Type"] = "Accounting"
            entry["Supplier"] = "Ecovis"
            entry["Description"] = "Accountant monthly fees"
            filled = True
        if "GAS" in desc:
            entry["Type"] = "Project management"
            entry["Supplier"] = "Transportation"
            entry["Description"] = "Gas station"
            filled = True
        if "DRAKAKIS" in desc:
            entry["Type"] = "Project management"
            entry["Supplier"] = "Drakakis Tours"
            entry["Description"] = "Car rent fees"
            filled = True
        if "FLIGHT" in desc or "AEGEAN" in desc:
            entry["Type"] = "Project management"
            entry["Supplier"] = "Transportation"
            entry["Description"] = "Flight"
            filled = True
        if any(word in desc for word in ["DINNER", "FOOD", "CAFE", "COFFEE", "LUNCH", "BREAKFAST"]):
            entry["Type"] = "General"
            entry["Supplier"] = "F&B"
            entry["Description"] = "F&B"
            filled = True
        if "GOOGLE" in desc:
            entry["Type"] = "Marketing"
            entry["Supplier"] = "Marketing"
            entry["Description"] = "Marketing Services fee"
            filled = True
        if "CRM" in desc:
            entry["Type"] = "Marketing"
            entry["Supplier"] = "reWire"
            entry["Description"] = "CRM"
            filled = True
        if "UBER" in desc or "TAXI" in desc:
            entry["Type"] = "Project management"
            entry["Supplier"] = "Transportation"
            entry["Description"] = "Athens Taxi"
            filled = True
        if "OPENAI" in desc:
            entry["Type"] = "General"
            entry["Supplier"] = "Office expenses"
            entry["Description"] = "Office expense"
            filled = True
        if "TAG" in desc:
            entry["Type"] = "Architect"
            entry["Supplier"] = "TAG ARCHITECTS"
            if "SUP" in desc:
                entry["Description"] = "Supervision"
            else:
                entry["Description"] = "Planning"
            filled = True
        if "OASA" in desc:
            entry["Type"] = "Project management"
            entry["Supplier"] = "Transportation"
            entry["Description"] = "Transportation"
            filled = True
        if any(term in desc for term in ["MANAGEMENT", "MANAG.", "MGMT", "MNGMT"]) and row['ΠΟΣΟ'] in [-1550, -1550.00, -1550.0, 1550.00, 1550.0, 1550]:
            entry["Type"] = "Worker 1"
            entry["Supplier"] = "Aiolos Athens"
            entry["Description"] = "management fees"
            filled = True
        if any(term in desc for term in ["COSM", "COSMOTE", "PHONE"]):
            entry["Type"] = "Utility Bills"
            entry["Supplier"] = "Cosmote"
            entry["Description"] = "Phone bill"
            filled = True

        if not filled:
            entry["Description"] = f"🟨 {entry['Description']}"

        results.append(entry)

    df = pd.DataFrame(results)
    if 'Original Description' in df.columns:
        original_col = df.pop('Original Description')
        df['Original Description'] = original_col
    return df

# --- RUN ---
if uploaded_file and project_type == "DIAKOFTI":
    if uploaded_file.name.endswith(".csv"):
        raw_df = pd.read_csv(uploaded_file, encoding="ISO-8859-7")
    else:
        raw_df = pd.read_excel(uploaded_file)

    result_df = process_file(raw_df)

    to_download = BytesIO()
    result_df.to_excel(to_download, index=False, engine='openpyxl')
    st.download_button(
        label="Download Processed File",
        data=to_download.getvalue(),
        file_name=f"diakofti_processed_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

elif uploaded_file and project_type == "ATHENS":
    raw_df = pd.read_excel(uploaded_file)
    result_df = process_athens_file(raw_df)

    to_download = BytesIO()
    result_df.to_excel(to_download, index=False, engine='openpyxl')
    st.download_button(
        label="Download Processed File",
        data=to_download.getvalue(),
        file_name=f"athens_processed_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
