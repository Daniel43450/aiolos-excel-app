import streamlit as st
import pandas as pd
import re
import datetime
from io import BytesIO
from docx import Document
import json
import os

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Aiolos Financial Tools",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CUSTOM CSS - CLEAN & MODERN DESIGN
# ============================================
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Reset and base styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container */
    .main {
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header with logo */
    .app-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 2rem;
    }
    
    .logo-container {
        flex-shrink: 0;
    }
    
    .logo-container img {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 3px solid rgba(255,255,255,0.3);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .header-text {
        flex-grow: 1;
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Navigation tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: white;
        padding: 0.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 1.5rem;
        background: transparent;
        border-radius: 8px;
        font-weight: 500;
        color: #666;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f8f9fa;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    
    /* Cards */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        margin-bottom: 1.5rem;
    }
    
    .info-card h3 {
        margin-top: 0;
        color: #333;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    /* Template preview */
    .template-preview {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 2px solid #e0e0e0;
        text-align: center;
    }
    
    .template-preview img {
        max-width: 100%;
        border-radius: 8px;
    }
    
    /* Metrics */
    .metric-container {
        display: flex;
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-box {
        flex: 1;
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #f0f0f0;
        text-align: center;
        transition: transform 0.2s;
    }
    
    .metric-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(30, 60, 114, 0.4);
    }
    
    /* File uploader */
    .stFileUploader {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        border: 2px dashed #e0e0e0;
        transition: all 0.3s;
    }
    
    .stFileUploader:hover {
        border-color: #2a5298;
        background: #fafbff;
    }
    
    /* Success/Warning messages */
    .success-msg {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #1a5f3f;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .warning-msg {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        color: #8b5a00;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .info-msg {
        background: linear-gradient(135deg, #a8d8ff 0%, #86c5ff 100%);
        color: #004085;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    /* Data table */
    .dataframe {
        border: none !important;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe thead {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    
    .dataframe tbody tr:hover {
        background: #f8f9fa;
    }
    
    /* Receipt table */
    .receipt-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }
    
    .receipt-table th {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
    }
    
    .receipt-table td {
        padding: 0.75rem;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .receipt-table tr:hover {
        background: #f8f9fa;
    }
    
    /* Action buttons in table */
    .action-button {
        background: #dc3545;
        color: white;
        border: none;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        cursor: pointer;
    }
    
    .action-button:hover {
        background: #c82333;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INITIALIZE SESSION STATE
# ============================================
if 'receipts_db' not in st.session_state:
    st.session_state.receipts_db = []

if 'invoices_db' not in st.session_state:
    st.session_state.invoices_db = []

# ============================================
# HEADER WITH LOGO
# ============================================
st.markdown("""
<div class="app-header">
    <div class="logo-container">
        <img src="https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG" alt="Aiolos Logo">
    </div>
    <div class="header-text">
        <h1 class="app-title">Aiolos Financial Tools</h1>
        <p class="app-subtitle">Smart financial management made simple</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================
def find_all_plots(description):
    """Find all plot references in description"""
    PLOTS = [
        'Y1', 'Y2', 'Y3', 'Y6', 'Y4-7', 'Y8', 'R2', 'R4', 'B5', 'G2',
        'R5A', 'R5B', 'R5C', 'R5D', 'W2', 'W8', 'B6', 'G1', 'G12', 'G13', 'B9-10-11'
    ]
    found = []
    for plot in PLOTS:
        if re.search(rf"(?<!\\w){re.escape(plot)}(?!\\w)", description):
            found.append(plot)
    return found

# ============================================
# VILLA OWNERS DATABASE
# ============================================
VILLA_OWNERS = {
    ("Y1", "Villa 1"): "George Bezerianos",
    ("Y1", "Villa 2"): "Shelley Furman Assa",
    ("Y2", "Villa 1"): "Shimrit Bourla",
    ("Y2", "Villa 2"): "Chen Arad",
    ("Y3", "Villa 1"): "Ronen Doron Aviram",
    ("Y3", "Villa 2"): "Ronen Ofec",
    ("Y3", "Villa 3"): "Eli Malka",
    ("Y3", "Villa 4"): "Ran Hai",
    ("Y3", "Villa 5"): "Eliyahu Ovadia",
    ("Y4-7", "Villa 9"): "Elad Shimon Nissenholtz",
    ("Y4-7", "Villa 10"): "Dan Dikanoff",
    ("G2", "Villa 1"): "Ester Danziger",
    ("G2", "Villa 2"): "Gil Bar el",
    ("G2", "Villa 3"): "Michael Gurevich",
    ("G2", "Villa 4"): "Tal Goldner-Gurevich",
    ("G2", "Villa 5"): "Alexander Gurevich",
    ("G2", "Villa 6"): "Linkova Oksana M",
    ("G2", "Villa 7"): "Ofir Laor",
    ("G2", "Villa 8"): "Patrice Daniel Giami",
    ("G13", "Villa 1"): "Nir Goldberg",
    ("G13", "Villa 2"): "Nir Goldberg",
    ("G13", "Villa 3"): "Keren Goldberg",
    ("G13", "Villa 4"): "Keren Goldberg",
    ("G13", "Villa 5"): "Rachel Goldberg Keidar",
    ("R4", "Villa 1"): "Itah Ella",
}

# ============================================
# DIAKOFTI PROCESSING FUNCTION
# ============================================
def process_diakofti_file(df):
    """Process Diakofti format files"""
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
        
        # ============================================
        # 🔴 DIAKOFTI RULES - ADD YOUR RULES HERE
        
        if "COM POI" in desc or "COM POO" in desc:
            entry["Type"] = "Bank"
            entry["Supplier"] = "Bank"
            entry["Description"] = "Bank fees"
            filled = True

        if "EDEN" in desc:
            entry["Type"] = "Project management"
            entry["Supplier"] = "Accommodation"
            entry["Description"] = "Hotel"
            filled = True

        if "ALL PLOTS MARKETING" in desc:
            entry["Type"] = "Marketing"
            entry["Supplier"] = "Marketing"
            entry["Description"] = "Marketing Services fee"
            filled = True

        if "CALEN" in desc or "HARD COST" in desc:
            entry["Expenses Type"] = "Hard Cost"
            entry["Type"] = "Contractor"
            entry["Supplier"] = "Calen"
            entry["Description"] = "Construction works"
            filled = True

        if "SUPERVISION" in desc:
            entry["Type"] = "Supervision"
            entry["Supplier"] = "TAG ARCHITECTS"
            entry["Description"] = "Supervision"
            filled = True

        if "HOLIDAYS TEL" in desc:
            entry["Type"] = "Project management"
            entry["Supplier"] = "Transportation"
            entry["Description"] = "Flight"
            filled = True

        if "EL AL" in desc:
            entry["Type"] = "Project management"
            entry["Supplier"] = "Transportation"
            entry["Description"] = "Flight"
            filled = True

        if any(keyword in desc.upper() for keyword in ["FACEBOOK", "FACEBK", "FB.ME", "META"]):
            entry["Type"] = "Marketing"
            entry["Supplier"] = "Marketing"
            entry["Description"] = "Marketing Services fee"
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

        if "TONY S" in desc or "Tony S" in desc or "tony s" in desc or "eat" in desc or "EAT" in desc:
            entry["Type"] = "General"
            entry["Supplier"] = "F&B"
            entry["Description"] = "F&B"
            filled = True


        if any(word in desc for word in ["AEGEANWEB", "AEGEAN", "OLYMPIC", "SKY", "ISRAIR", "WIZZ"]):
            entry["Type"] = "Project management"
            entry["Supplier"] = "Transportation"
            entry["Description"] = "Flight"
            filled = True

        if any(word in desc for word in ["DINNER", "FOOD", "CAFE", "COFFEE", "LUNCH", "BREAKFAST"]):
            entry["Type"] = "General"
            entry["Supplier"] = "F&B"
            entry["Description"] = "F&B"
            filled = True

        if ("broker" in desc or "Broker" in desc or "BROKER" in desc) and (
            "villa 1" in desc or "Villa 1" in desc or "VILLA 1" in desc):
            entry["Type"] = "Brokers"
            entry["Supplier"] = "Buyer Villa 1"
            entry["Description"] = "Broker fees"
            filled = True

        if ("broker" in desc or "Broker" in desc or "BROKER" in desc) and (
            "villa 2" in desc or "Villa 2" in desc or "VILLA 2" in desc):
            entry["Type"] = "Brokers"
            entry["Supplier"] = "Buyer Villa 2"
            entry["Description"] = "Broker fees"
            filled = True

        if "RF919086180000334" in desc:
            entry["Plot"] = "R4"
            entry["Expenses Type"] = "Soft Cost"
            entry["Type"] = "Utility Bills"
            entry["Supplier"] = "Municipality"
            entry["Description"] = "Electricity"
            filled = True


        if ("broker" in desc or "Broker" in desc or "BROKER" in desc) and (
            "villa 3" in desc or "Villa 3" in desc or "VILLA 3" in desc):
            entry["Type"] = "Brokers"
            entry["Supplier"] = "Buyer Villa 3"
            entry["Description"] = "Broker fees"
            filled = True

        if ("broker" in desc or "Broker" in desc or "BROKER" in desc) and (
            "villa 4" in desc or "Villa 4" in desc or "VILLA 4" in desc):
            entry["Type"] = "Brokers"
            entry["Supplier"] = "Buyer Villa 4"
            entry["Description"] = "Broker fees"
            filled = True

        if ("broker" in desc or "Broker" in desc or "BROKER" in desc) and (
            "villa 5" in desc or "Villa 5" in desc or "VILLA 5" in desc):
            entry["Type"] = "Brokers"
            entry["Supplier"] = "Buyer Villa 5"
            entry["Description"] = "Broker fees"
            filled = True

        if ("broker" in desc or "Broker" in desc or "BROKER" in desc) and (
            "villa 6" in desc or "Villa 6" in desc or "VILLA 6" in desc):
            entry["Type"] = "Brokers"
            entry["Supplier"] = "Buyer Villa 6"
            entry["Description"] = "Broker fees"
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

        if "RF91908618000033404472101" in desc or "PROT-RF549086180000334" in desc:
            entry["Type"] = "Utility Bills"
            entry["Supplier"] = "Municipality"
            entry["Description"] = "Electricity"
            entry["Plot"] = "G2"
            filled = True

        if "RF38908618000033404445701" in desc or "RF389086180000334044" in desc:  
            entry["Type"] = "Utility Bills"
            entry["Supplier"] = "Municipality"
            entry["Description"] = "Electricity"
            entry["Plot"] = "Y3"
            filled = True

        if "RF91908618000033404472101" in desc or "PROT-919086180000334" in desc:
            entry["Type"] = "Utility Bills"
            entry["Supplier"] = "Municipality"
            entry["Description"] = "Electricity"
            entry["Plot"] = "R4"
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

        if "ΔΗΜΟ-RF369029090000097" in desc:
            entry["Type"] = "Utility Bills"
            entry["Supplier"] = "Municipality"
            entry["Description"] = "Water"
            entry["Plot"] = "Y3"
            filled = True


        if any(term in desc for term in ["MANAGEMENT", "MANAG.", "MGMT", "MNGMT"]) and row['ΠΟΣΟ'] in [-1550, -1550.00, -1550.0, 1550.00, 1550.0, 2055, 2055.0, 2057.0, 1550]:
            entry["Type"] = "Worker 1"
            entry["Supplier"] = "Aiolos Athens"
            entry["Description"] = "management fees"
            filled = True

        if any(term in desc for term in ["COSM", "COSMOTE", "PHONE"]):
            entry["Type"] = "Utility Bills"
            entry["Supplier"] = "Cosmote"
            entry["Description"] = "Phone bill"
            filled = True


        # END OF DIAKOFTI RULES
        # ============================================
        
        if not filled:
            entry["Description"] = f"🟨 {entry['Description']}"
        
        results.append(entry)
    
    return pd.DataFrame(results)

# ============================================
# ATHENS PROCESSING FUNCTION
# ============================================
def process_athens_file(df):
    """Process Athens format files"""
    df = df.copy()
    df['Ημερομηνία'] = pd.to_datetime(df['Ημερομηνία'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Περιγραφή'])
    
    results = []
    for _, row in df.iterrows():
        original_desc = str(row['Περιγραφή'])
        desc = original_desc.upper()
        amount = abs(float(str(row['Ποσό συναλλαγής']).replace(',', '.')))
        
        entry = {
            "Date": row['Ημερομηνία'].strftime('%d/%m/%Y') if not pd.isnull(row['Ημερομηνία']) else '',
            "Income/Outcome": "Income" if row['Ποσό συναλλαγής'] > 0 else "Outcome",
            "Expenses Type": "Soft Cost",
            "Location": "All Projects",
            "Project": "All Projects",
            "Supplier": "",
            "Type": "",
            "Description": desc,
            "Income": amount if row['Ποσό συναλλαγής'] > 0 else "",
            "Outcome": -amount if row['Ποσό συναλλαγής'] < 0 else "",
            "Total": amount if row['Ποσό συναλλαγής'] > 0 else -amount,
            "Balance": "",
            "Repayment": "",
            "Original Description": original_desc
        }
        
        filled = False
        
        # ============================================
        # 🔵 ATHENS RULES - ADD YOUR RULES HERE
        if any(word in desc for word in ["DINNER", "FOOD", "CAFE", "COFFEE", "LUNCH", "BREAKFAST", "ΦΑΓΗΤΟ", "ΕΣΤΙΑΤΟΡΙΟ", "ΚΑΦΕ"]):
            entry["Type"] = "F&B"
            entry["Supplier"] = "General"
            entry["Description"] = "F&B"
            filled = True

        if "TEKA" in desc and round(amount, 2) == 76.66:
            entry["Supplier"] = "Worker 1"
            entry["Type"] = "Operation cost"
            entry["Description"] = "TEKA"
            filled = True

        if "BAGELDB" in desc:
            entry["Type"] = "Marketing"
            entry["Supplier"] = "BagelDB"
            entry["Description"] = "Website"
            filled = True

        if any(variant in desc for variant in ["AP MICHALOPOULOS SIA", "Ap Michalopoulos Sia", "ap michalopoulos sia"]):
            entry["Type"] = "F&B"
            entry["Supplier"] = "General"
            entry["Description"] = "F&B"
            filled = True
           
        if any(word in desc for word in ["AVIS", "HERTZ", "SIXT", "CAR RENTAL"]):
            entry["Type"] = "Transportation"
            entry["Supplier"] = "Transportation"
            entry["Description"] = "Car rental"
            entry["Plot"] = "All Projects"
            filled = True
           
        if "COSMOTE" in desc:
            entry["Location"] = "Mobee"
            entry["Project"] = "Mobee"
            entry["Supplier"] = "Cosmote"
            entry["Type"] = "Project Management"
            entry["Description"] = "Office expenses"
            filled = True

           
        if any(word in desc for word in ["BAKERY", "CAFFE", "CAFE", "EAT", "BEVERAGE", "PIZA", "BURGER"]):
            entry["Type"] = "F&B"
            entry["Supplier"] = "General"
            entry["Description"] = "F&B"
            filled = True

        if any(keyword in desc for keyword in ["WEBCCDOMAINCOM", "webccdomaincom", "Webccdomaincom"]):
            entry["Type"] = "Marketing"
            entry["Supplier"] = "BagelDB"
            entry["Description"] = "Website"
            entry["Repayment"] = "DOMAIN"
            filled = True
           
        if round(amount, 2) == 496.00 and any(word in desc for word in ["ECOVIS", "FEE", "FEES"]):
            entry["Supplier"] = "Accountant"
            entry["Type"] = "Ecovis"
            entry["Description"] = "Accountant monthly fees"
            filled = True

        if abs(row['Ποσό συναλλαγής']) == 256.41 and row['Ποσό συναλλαγής'] < 0:
            entry["Type"] = "Tax"
            entry["Supplier"] = "Authorities"
            entry["Description"] = "EFKA"
            entry["Repayment"] = "UDI EFKA"
            filled = True
           
        if "MANAGEMENT FEE" in desc or row['Ποσό συναλλαγής'] in [-1810, 1810, -1810.00, 1810.00]:
            entry["Type"] = "Mobee Management"
            entry["Supplier"] = "Konstantinos"
            entry["Description"] = "Management fee"
            filled = True

        if "ΠΡΟΜΗΘΕΙΕΣ ΕΞΟΔΑ" in desc and amount <= 5:
            entry["Type"] = "Bank fees"
            entry["Supplier"] = "Bank"
            entry["Description"] = "Bank fees"
            filled = True

        if "AIOLOS DIAKOFTI" in desc and 1520 <= amount <= 1570:
            entry["Supplier"] = "Aiolos Diakofti"
            entry["Type"] = "Operation cost"
            entry["Description"] = "Reimbursement of expenses"
            filled = True

        if ("ΚΑΛΛΙΦΡΟΝΑ 3" in desc or "ΚΑΛΛΙΦΡΟΝΑ3" in desc) and row['Ποσό συναλλαγής'] > 0:
            entry["Type"] = "Mobee Management"
            entry["Supplier"] = "Kalliforna"
            entry["Description"] = "Management fee"
            entry["Location"] = "Mobee"
            filled = True
           
        if "ΠΛΗΡΩΜΗ ΕΦΚΑ ΕΡΓΟΔΟΤΙΚΕΣ ΕΙΣΦΟΡΕΣ" in desc:
            entry["Type"] = "Tax"
            entry["Supplier"] = "Authorities"
            entry["Description"] = "EFKA"
            filled = True

        if "PLAKENTIA" in desc:
            entry["Type"] = "Transportation"
            entry["Supplier"] = "General"
            entry["Description"] = "Metro"
            filled = True

        if "MICROSOFT" in desc:
            entry["Type"] = "Project Management"
            entry["Supplier"] = "Microsoft"
            entry["Description"] = "Office expenses"
            filled = True

        if "LEFKES VILLAS PROJECT MONOPROSOPI" in desc:
            entry["Supplier"] = "Lefkes Villas"
            entry["Type"] = "Project Management"
            entry["Description"] = "Management fee"

        if "LEFKES" in desc:
            entry["Location"] = "Lefkes"

        if "BEN SHAHAR" in desc:
            entry["Supplier"] = "Ben Shahar"
            entry["Type"] = "Project Management"
            entry["Description"] = "Management fee"
            entry["Location"] = "Lefkes"
                 
        if "PARKING" in desc:
            entry["Type"] = "Transportation"
            entry["Supplier"] = "Parking"
            entry["Description"] = "Parking"
            filled = True

        if "ECOVIS" in desc:
            entry["Type"] = "Ecovis"
            entry["Supplier"] = "Accountant"
            entry["Description"] = "Accountant monthly fees"
            filled = True

        if row['Ποσό συναλλαγής'] == 4960:
            entry["Type"] = "Project Management"
            entry["Supplier"] = "Lefkes Villas"
            entry["Description"] = "Management fee"
            entry["Location"] = "Lefkes"
            entry["Expenses Type"] = "Soft cost"
            filled = True

        if "HAREL" in desc:
            entry["Type"] = "Project Management"
            entry["Supplier"] = "General"
            entry["Description"] = "Office expenses"
            filled = True

        if "SHELL" in desc:
            entry["Type"] = "Transportation"
            entry["Supplier"] = "General"
            entry["Description"] = "Gas station"
            filled = True

        if "OASA" in desc:
            entry["Type"] = "Transportation"
            entry["Supplier"] = "General"
            entry["Description"] = "Metro"
            filled = True

        if "WORKER 1" in desc:
            entry["Type"] = "Operation cost"
            entry["Supplier"] = "Worker 1"
            entry["Description"] = "Salary"
            filled = True

        if any(word in desc for word in ["AEGEANWEB", "AEGEAN", "OLYMPIC", "SKY", "ISRAIR", "WIZZ"]):
            entry["Type"] = "Transportation"
            entry["Supplier"] = "General"
            entry["Description"] = "Flight"
            filled = True

        if "PARKAROUND" in desc:
            entry["Type"] = "Transportation"
            entry["Supplier"] = "Parking"
            entry["Description"] = "Parking"
            filled = True

        if any(word in desc for word in ["ATTIKI"]):
            entry["Type"] = "Transportation"
            entry["Supplier"] = "General"
            entry["Description"] = "Toll road"
            filled = True

        if any(word in desc for word in ["UBER", "UBR"]):
            entry["Type"] = "Transportation"
            entry["Supplier"] = "General"
            entry["Description"] = "Uber"
            filled = True

        if "GOOGLE" in desc:
            entry["Type"] = "Marketing"
            entry["Supplier"] = "Google"
            entry["Description"] = "Campaign"
            filled = True

        if "PETRELION" in desc:
            entry["Type"] = "Transportation"
            entry["Supplier"] = "General"
            entry["Description"] = "Gas station"
            filled = True

        if any(word in desc for word in ["ΠΡΟΜΗΘ", "ΜΗΝ", "ΠΑΡ", "ΕΞΟΔΑ"]) and amount <= 5:
            entry["Type"] = "Bank"
            entry["Supplier"] = "Bank"
            entry["Description"] = "Bank fees"
            filled = True


        # END OF ATHENS RULES
        # ============================================
        
        if not filled:
            entry["Description"] = f"🟨 {entry['Description']}"
        
        results.append(entry)
    
    result_df = pd.DataFrame(results)
    
    # Reorder columns
    column_order = [
        "Date", "Income/Outcome", "Expenses Type", "Location", "Project",
        "Supplier", "Type", "Description", "Income", "Outcome", "Total",
        "Balance", "Repayment", "Original Description"
    ]
    
    return result_df[column_order]

# ============================================
# MAIN TABS
# ============================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Excel Classifier", 
    "📝 Payment Instructions", 
    "🧾 Invoices",
    "📋 Receipts Database",
    "ℹ️ Help"
])

# ============================================
# TAB 1: EXCEL CLASSIFIER
# ============================================
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Excel Classifier")
        st.markdown("Upload your financial Excel file to automatically categorize and organize transactions.")
        
        # File format selection
        format_type = st.selectbox(
            "Select File Format",
            ["DIAKOFTI", "ATHENS"],
            help="Choose the format that matches your data structure"
        )
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload Excel or CSV File",
            type=["xlsx", "csv", "xls"],
            help="Drag and drop or click to browse"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📌 Quick Guide")
        st.markdown("""
        **Formats:**
        - **DIAKOFTI**: Plot-based transactions
        - **ATHENS**: Office transactions
        
        **Supported Files:**
        - Excel (.xlsx, .xls)
        - CSV files
        
        **Output:**
        - Auto-categorized data
        - Entries needing review marked with 🟨
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Process uploaded file
    if uploaded_file:
        st.markdown('<div class="success-msg">✅ File uploaded successfully!</div>', unsafe_allow_html=True)
        
        # Process button
        if st.button("🚀 Process File", use_container_width=True, key="process_excel"):
            with st.spinner("Processing your data..."):
                try:
                    # Read file
                    if uploaded_file.name.endswith('.csv'):
                        if format_type == "DIAKOFTI":
                            df = pd.read_csv(uploaded_file, encoding="ISO-8859-7")
                        else:
                            df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    # Process based on format
                    if format_type == "DIAKOFTI":
                        result_df = process_diakofti_file(df)
                    else:
                        result_df = process_athens_file(df)
                    
                    # Calculate metrics
                    total_entries = len(result_df)
                    needs_review = result_df['Description'].str.contains('🟨').sum()
                    auto_classified = total_entries - needs_review
                    success_rate = (auto_classified / total_entries * 100) if total_entries > 0 else 0
                    
                    # Display metrics
                    st.markdown("""
                    <div class="metric-container">
                        <div class="metric-box">
                            <div class="metric-value">{}</div>
                            <div class="metric-label">Total Entries</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-value">{}</div>
                            <div class="metric-label">Auto-Classified</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-value">{}</div>
                            <div class="metric-label">Need Review</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-value">{:.1f}%</div>
                            <div class="metric-label">Success Rate</div>
                        </div>
                    </div>
                    """.format(total_entries, auto_classified, needs_review, success_rate), unsafe_allow_html=True)
                    
                    # Show preview
                    st.markdown("### 📋 Data Preview")
                    st.dataframe(result_df.head(10), use_container_width=True)
                    
                    # Download button
                    output = BytesIO()
                    result_df.to_excel(output, index=False, engine='openpyxl')
                    output.seek(0)
                    
                    st.download_button(
                        label="📥 Download Processed File",
                        data=output,
                        file_name=f"{format_type.lower()}_processed_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")

# ============================================
# TAB 2: PAYMENT INSTRUCTIONS
# ============================================

with tab2:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Generate Payment Instructions")

        # Project selection
        project = st.selectbox(
            "Select Project",
            sorted(set(k[0] for k in VILLA_OWNERS)),
            help="Choose the project plot",
            key="payment_project"
        )

        # Villa selection
        villa_options = sorted(set(k[1] for k in VILLA_OWNERS if k[0] == project))
        villa = st.selectbox(
            "Select Villa",
            villa_options,
            help="Select the villa number",
            key="payment_villa"
        )

        # Display owner name
        client_name = VILLA_OWNERS.get((project, villa), "")
        if client_name:
            st.markdown(f'<div class="info-msg">👤 <strong>Owner:</strong> {client_name}</div>', unsafe_allow_html=True)

        # Payment details
        st.markdown("### 💳 Payment Details")
        payment_order = st.text_input("Payment Order Number", placeholder="e.g., 12345", key="payment_order")
        amount = st.text_input("Amount in Euro (€)", placeholder="e.g., 5000", key="payment_amount")
        extra_text = st.text_area("Additional Notes (Optional)", placeholder="Any additional payment information...", key="payment_notes")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="template-preview">', unsafe_allow_html=True)
        st.markdown("### 📄 Template Preview")
        st.markdown("See how your payment instruction will look:")
        st.image("https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/payment_order_PNG.png", 
                 caption="Payment Instruction Template",
                 use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Generate payment instruction
    if st.button("📄 Generate Payment Instruction", use_container_width=True, key="generate_payment"):
        if payment_order and amount:
            try:
                template = Document("default_template.docx")

                # Replace placeholders
                for p in template.paragraphs:
                    p.text = p.text.replace("{{date}}", datetime.datetime.now().strftime("%d/%m/%Y"))
                    p.text = p.text.replace("{{plot}}", project)
                    p.text = p.text.replace("{{villa_no}}", villa)
                    p.text = p.text.replace("{{client_name}}", client_name)
                    p.text = p.text.replace("{{payment_order_number}}", payment_order)
                    p.text = p.text.replace("{{sum}}", amount)
                    p.text = p.text.replace("{{Extra Payment text}}", extra_text)

                # Save to buffer
                buffer = BytesIO()
                template.save(buffer)
                buffer.seek(0)

                filename = f"Payment_Instruction_{project}_{villa}_Order_{payment_order}.docx"

                # ✅ Store in history list
                instruction_data = {
                    "date": datetime.datetime.now().strftime("%d/%m/%Y"),
                    "project": project,
                    "villa": villa,
                    "client_name": client_name,
                    "payment_order": payment_order,
                    "amount": amount,
                    "notes": extra_text
                }
                if 'payment_instructions_db' not in st.session_state:
                    st.session_state.payment_instructions_db = []
                st.session_state.payment_instructions_db.append(instruction_data)

                # Also store for invoice form
                st.session_state.last_payment = instruction_data

                # Success message and download
                st.markdown('<div class="success-msg">✅ Payment instruction generated successfully!</div>', unsafe_allow_html=True)

                st.download_button(
                    label="📥 Download Payment Instruction",
                    data=buffer,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

                st.markdown("---")
                st.markdown("### 🧾 Next Step: Create Invoice")
                st.info("Payment instruction created! You can now create an invoice for this payment in the Invoices tab.")

            except FileNotFoundError:
                st.error("❌ Template file 'default_template.docx' not found. Please add it to the app directory.")
            except Exception as e:
                st.error(f"❌ Error generating payment instruction: {str(e)}")
        else:
            st.warning("⚠️ Please fill in Payment Order Number and Amount")

# ============================================
# TAB 3: INVOICES
# ============================================
# ============================================
# TAB 3: INVOICES
# ============================================

# אתחול מאגר הוראות תשלום (אם לא קיים)
if 'payment_instructions_db' not in st.session_state:
    st.session_state.payment_instructions_db = []

st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.markdown("### 🧾 Invoice Generator")

# 🗂️ הצגת הוראות תשלום מהעבר
st.markdown("### 🗂️ Past Payment Instructions")

if st.session_state.payment_instructions_db:
    for idx, inst in enumerate(st.session_state.payment_instructions_db):
        with st.expander(f"📄 {inst['project']} - Villa {inst['villa']} | €{inst['amount']} | Order #{inst['payment_order']}"):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                - **Date:** {inst['date']}
                - **Client:** {inst['client_name']}
                - **Payment Order #:** {inst['payment_order']}
                - **Amount:** €{inst['amount']}
                - **Notes:** {inst['notes'] or '–'}
                """)
                if st.button("📤 Load into Invoice Form", key=f"load_instruction_{idx}"):
                    st.session_state.last_payment = inst
                    st.success("✅ Loaded into invoice form!")
            with col2:
                if st.button("🗑️ Delete", key=f"delete_instruction_{idx}"):
                    st.session_state.payment_instructions_db.pop(idx)
                    st.rerun()
else:
    st.info("📭 No past payment instructions saved yet.")

st.markdown("---")

# הכנה לטופס החשבונית
if 'last_payment' in st.session_state:
    st.markdown('<div class="info-msg">📌 Loaded payment instruction: Fields auto-filled below.</div>', unsafe_allow_html=True)
    default_project = st.session_state.last_payment['project']
    default_villa = st.session_state.last_payment['villa']
    default_amount = st.session_state.last_payment['amount']
    default_payment_order = st.session_state.last_payment['payment_order']
else:
    default_project = sorted(set(k[0] for k in VILLA_OWNERS))[0]
    default_villa = None
    default_amount = ""
    default_payment_order = ""

col1, col2 = st.columns([3, 2])

with col1:
    invoice_project = st.selectbox(
        "Project",
        sorted(set(k[0] for k in VILLA_OWNERS)),
        index=sorted(set(k[0] for k in VILLA_OWNERS)).index(default_project) if default_project else 0,
        key="invoice_project"
    )

    villa_options_invoice = sorted(set(k[1] for k in VILLA_OWNERS if k[0] == invoice_project))
    invoice_villa = st.selectbox(
        "Villa",
        villa_options_invoice,
        index=villa_options_invoice.index(default_villa) if default_villa in villa_options_invoice else 0,
        key="invoice_villa"
    )

    invoice_client = VILLA_OWNERS.get((invoice_project, invoice_villa), "")
    if invoice_client:
        st.markdown(f'<div class="info-msg">👤 <strong>Client:</strong> {invoice_client}</div>', unsafe_allow_html=True)

    invoice_number = st.text_input("Invoice Number", value=default_payment_order, placeholder="INV-001", key="invoice_number")
    invoice_amount = st.text_input("Amount (€)", value=default_amount, placeholder="5000", key="invoice_amount")
    invoice_date = st.date_input("Invoice Date", value=datetime.date.today(), key="invoice_date")
    invoice_notes = st.text_area("Notes/Description", placeholder="Payment received for...", key="invoice_notes")

with col2:
    st.markdown("### 📊 Invoice Preview")
    if invoice_number and invoice_amount:
        st.markdown(f"""
        **Invoice #:** {invoice_number}  
        **Date:** {invoice_date}  
        **Client:** {invoice_client}  
        **Project:** {invoice_project} - {invoice_villa}  
        **Amount:** €{invoice_amount}  
        """)

# יצירת החשבונית
if st.button("🧾 Generate Invoice", use_container_width=True, key="generate_invoice"):
    if invoice_number and invoice_amount:
        invoice_data = {
            "invoice_number": invoice_number,
            "date": str(invoice_date),
            "project": invoice_project,
            "villa": invoice_villa,
            "client": invoice_client,
            "amount": invoice_amount,
            "notes": invoice_notes,
            "timestamp": datetime.datetime.now().isoformat()
        }

        st.session_state.invoices_db.append(invoice_data)

        receipt_data = {
            "type": "Invoice",
            "number": invoice_number,
            "date": str(invoice_date),
            "project": invoice_project,
            "villa": invoice_villa,
            "client": invoice_client,
            "amount": invoice_amount,
            "notes": invoice_notes,
            "timestamp": datetime.datetime.now().isoformat()
        }

        st.session_state.receipts_db.append(receipt_data)

        st.markdown('<div class="success-msg">✅ Invoice generated and saved to database!</div>', unsafe_allow_html=True)

        invoice_content = f"""
INVOICE
========================================
Invoice Number: {invoice_number}
Date: {invoice_date}
----------------------------------------
Bill To:
{invoice_client}
{invoice_project} - {invoice_villa}
----------------------------------------
Amount Due: €{invoice_amount}
----------------------------------------
Notes:
{invoice_notes}
========================================
Generated by Aiolos Financial Tools
        """

        st.download_button(
            label="📥 Download Invoice (Text)",
            data=invoice_content,
            file_name=f"Invoice_{invoice_number}_{invoice_date}.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.warning("⚠️ Please fill in Invoice Number and Amount")

st.markdown('</div>', unsafe_allow_html=True)


# ============================================
# TAB 4: RECEIPTS DATABASE
# ============================================
with tab4:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### 📋 All Receipts & Invoices Database")
    
    # Combine all receipts and invoices
    all_records = st.session_state.receipts_db
    
    if all_records:
        # Create DataFrame for display
        df_records = pd.DataFrame(all_records)
        
        # Summary metrics
        total_records = len(df_records)
        total_amount = sum(float(r['amount']) for r in all_records if r['amount'])
        unique_projects = len(set(r['project'] for r in all_records))
        
        st.markdown("""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-value">{}</div>
                <div class="metric-label">Total Records</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">€{:,.2f}</div>
                <div class="metric-label">Total Amount</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{}</div>
                <div class="metric-label">Projects</div>
            </div>
        </div>
        """.format(total_records, total_amount, unique_projects), unsafe_allow_html=True)
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_project = st.selectbox(
                "Filter by Project",
                ["All"] + sorted(set(r['project'] for r in all_records)),
                key="filter_project"
            )
        with col2:
            filter_villa = st.selectbox(
                "Filter by Villa",
                ["All"] + sorted(set(r['villa'] for r in all_records)),
                key="filter_villa"
            )
        with col3:
            filter_type = st.selectbox(
                "Filter by Type",
                ["All", "Invoice", "Payment Instruction"],
                key="filter_type"
            )
        
        # Apply filters
        filtered_records = all_records
        if filter_project != "All":
            filtered_records = [r for r in filtered_records if r['project'] == filter_project]
        if filter_villa != "All":
            filtered_records = [r for r in filtered_records if r['villa'] == filter_villa]
        if filter_type != "All":
            filtered_records = [r for r in filtered_records if r['type'] == filter_type]
        
        # Display table
        if filtered_records:
            st.markdown("### 📊 Records Table")
            
            # Create a more readable table
            for idx, record in enumerate(filtered_records):
                with st.expander(f"{record['type']} #{record['number']} - {record['project']} {record['villa']} - €{record['amount']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Date:** {record['date']}")
                        st.write(f"**Client:** {record['client']}")
                        st.write(f"**Amount:** €{record['amount']}")
                        if record['notes']:
                            st.write(f"**Notes:** {record['notes']}")
                    with col2:
                        if st.button(f"🗑️ Delete", key=f"delete_{idx}"):
                            st.session_state.receipts_db.pop(idx)
                            st.rerun()
        else:
            st.info("No records found with the selected filters.")
        
        # Export options
        st.markdown("---")
        st.markdown("### 📥 Export Options")
        
        # Export to Excel
        if st.button("📊 Export All to Excel", use_container_width=True):
            df_export = pd.DataFrame(all_records)
            output = BytesIO()
            df_export.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            
            st.download_button(
                label="📥 Download Excel File",
                data=output,
                file_name=f"receipts_database_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.info("📭 No receipts or invoices generated yet. Create your first one in the Payment Instructions or Invoices tab!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Clear database option
    st.markdown("---")
    st.markdown("### ⚠️ Database Management")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🗑️ Clear All Records", use_container_width=True):
            st.session_state.show_clear_confirm = True
    
    if 'show_clear_confirm' in st.session_state and st.session_state.show_clear_confirm:
        with col2:
            if st.button("✅ Confirm Clear", use_container_width=True):
                st.session_state.receipts_db = []
                st.session_state.invoices_db = []
                st.session_state.show_clear_confirm = False
                st.success("Database cleared successfully!")
                st.rerun()
        with col3:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_clear_confirm = False
                st.rerun()

# ============================================
# TAB 5: HELP
# ============================================
with tab5:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### 🔧 How to Use Aiolos Financial Tools")
    
    st.markdown("""
    #### 📊 Excel Classifier
    1. **Select Format**: Choose between DIAKOFTI (plot-based) or ATHENS (office) format
    2. **Upload File**: Upload your Excel or CSV file
    3. **Process**: Click the Process button to categorize transactions
    4. **Review**: Check entries marked with 🟨 - these need manual review
    5. **Download**: Download the processed file with all categorizations
    
    #### 📝 Payment Instructions
    1. **Select Villa**: Choose project and villa number
    2. **Enter Details**: Add payment order number and amount
    3. **Template Preview**: See how your document will look
    4. **Generate**: Click to create a Word document
    5. **Next Step**: Option to create an invoice for the payment
    
    #### 🧾 Invoices
    1. **Auto-fill**: If you created a payment instruction, details are pre-filled
    2. **Edit Details**: Adjust amount or add notes as needed
    3. **Generate**: Create invoice and save to database
    4. **Download**: Get a copy for your records
    
    #### 📋 Receipts Database
    1. **View All**: See all payment instructions and invoices
    2. **Filter**: Filter by project, villa, or type
    3. **Delete**: Remove individual records
    4. **Export**: Download entire database as Excel
    5. **Manage**: Clear database if needed
    
    #### 🔧 Adding Classification Rules
    To add classification rules, edit the code in the processing functions:
    - **DIAKOFTI Rules**: Look for the section marked "🔴 DIAKOFTI RULES"
    - **ATHENS Rules**: Look for the section marked "🔵 ATHENS RULES"
    
    #### 📞 Support
    For issues or questions, please contact the development team.
    
    ---
    
    ### 🏢 About Aiolos
    Aiolos Financial Tools is designed to streamline financial management for real estate projects,
    making it easy to process transactions, generate documents, and maintain records.
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Version info
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Version:** 3.0.0")
        st.markdown("**Last Updated:** " + datetime.datetime.now().strftime("%Y-%m-%d"))
    with col2:
        st.markdown("**Developed by:** Aiolos Team")
        st.markdown("**© 2024 Aiolos. All rights reserved.**")
