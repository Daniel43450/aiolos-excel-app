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

if 'payment_instructions_db' not in st.session_state:
    st.session_state.payment_instructions_db = []

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
        # Show template preview image from GitHub
        st.image("https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/payment_order_PNG.png", 
                 caption="Payment Instruction Template",
                 use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate payment instruction
    if st.button("📄 Generate Payment Instruction", use_container_width=True, key="generate_payment"):
        if payment_order and amount:
            try:
                # Note: You'll need to have the template file
                template = Document("default_tempate.docx")
                
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
                
                # שמור את ההוראה בהיסטוריה
                payment_instruction = {
                    "id": f"PI_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "project": project,
                    "villa": villa,
                    "client_name": client_name,
                    "payment_order": payment_order,
                    "amount": amount,
                    "notes": extra_text,
                    "created_date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                st.session_state.payment_instructions_db.append(payment_instruction)
                
                # עדיין שמור גם כ-last_payment לתאימות לאחור
                st.session_state.last_payment = payment_instruction
                
                st.markdown('<div class="success-msg">✅ Payment instruction generated successfully!</div>', unsafe_allow_html=True)
                
                st.download_button(
                    label="📥 Download Payment Instruction",
                    data=buffer,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                
                # Option to create invoice
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
# TAB 3: INVOICES  -> Receipt of Funds Generator
# ============================================
with tab3:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### 🧾 Receipt of Funds Generator")
    
    # ---------- Helpers for state ----------
    def _all_projects():
        return sorted(set(k[0] for k in VILLA_OWNERS))

    def _villas_for(project):
        return sorted(set(k[1] for k in VILLA_OWNERS if k[0] == project))

    def _ensure_form_state_defaults():
        # init once
        if 'receipt_project' not in st.session_state:
            st.session_state.receipt_project = _all_projects()[0]
        if 'receipt_villa' not in st.session_state:
            st.session_state.receipt_villa = _villas_for(st.session_state.receipt_project)[0]
        if 'receipt_payment_order' not in st.session_state:
            st.session_state.receipt_payment_order = ""
        if 'receipt_amount' not in st.session_state:
            st.session_state.receipt_amount = ""
        if 'receipt_date' not in st.session_state:
            st.session_state.receipt_date = datetime.date.today()
        if 'receipt_extra_text' not in st.session_state:
            st.session_state.receipt_extra_text = ""

    def _load_into_form_from_instruction(instr):
        # Fill widget state directly from selected instruction
        st.session_state.receipt_project = instr.get('project', _all_projects()[0]) or _all_projects()[0]
        # Make sure villa exists for project
        villas = _villas_for(st.session_state.receipt_project)
        v = instr.get('villa') if instr.get('villa') in villas else villas[0]
        st.session_state.receipt_villa = v
        st.session_state.receipt_payment_order = str(instr.get('payment_order', ''))
        st.session_state.receipt_amount = str(instr.get('amount', ''))
        st.session_state.receipt_date = datetime.date.today()
        st.session_state.receipt_extra_text = instr.get('notes', '')

    def _clear_form():
        first_project = _all_projects()[0]
        st.session_state.receipt_project = first_project
        st.session_state.receipt_villa = _villas_for(first_project)[0]
        st.session_state.receipt_payment_order = ""
        st.session_state.receipt_amount = ""
        st.session_state.receipt_date = datetime.date.today()
        st.session_state.receipt_extra_text = ""
        # Also clear any loaded instruction
        if 'selected_payment_instruction' in st.session_state:
            del st.session_state.selected_payment_instruction

    def _find_template_path():
        for pth in ["Receipt_of_Funds.docx", "/mnt/data/Receipt_of_Funds.docx"]:
            if os.path.exists(pth):
                return pth
        return None

    def _fill_template_docx(template_path, mapping):
        # Using python-docx: replacing paragraph & table text, then re-apply bold on title
        doc = Document(template_path)

        # paragraphs
        for p in doc.paragraphs:
            txt = p.text
            for k, v in mapping.items():
                txt = txt.replace(k, v)
            p.text = txt  # resets runs

        # tables
        for tbl in doc.tables:
            for row in tbl.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        txt = p.text
                        for k, v in mapping.items():
                            txt = txt.replace(k, v)
                        p.text = txt

        # keep title bold
        for p in doc.paragraphs:
            if p.text.strip().startswith("Receipt of Funds"):
                for run in p.runs:
                    run.bold = True
        return doc

    # ---------- Payment Instructions History ----------
    if st.session_state.payment_instructions_db:
        st.markdown("### 📋 Payment Instructions History")
        st.markdown('<div class="info-msg">💡 Select a payment instruction to auto-fill the receipt form</div>', unsafe_allow_html=True)
        
        cols_history = st.columns([0.5, 1, 1.5, 1.5, 1, 1, 0.5, 0.5])
        with cols_history[0]: st.write("**#**")
        with cols_history[1]: st.write("**Date**")
        with cols_history[2]: st.write("**Project**")
        with cols_history[3]: st.write("**Client**")
        with cols_history[4]: st.write("**Order#**")
        with cols_history[5]: st.write("**Amount**")
        with cols_history[6]: st.write("**Load**")
        with cols_history[7]: st.write("**Delete**")
        st.markdown("---")
        
        for idx, instruction in enumerate(reversed(st.session_state.payment_instructions_db)):
            actual_idx = len(st.session_state.payment_instructions_db) - 1 - idx
            cols_row = st.columns([0.5, 1, 1.5, 1.5, 1, 1, 0.5, 0.5])
            with cols_row[0]:
                st.write(f"{idx + 1}")
            with cols_row[1]:
                st.write(instruction['created_date'].split(' ')[0])
            with cols_row[2]:
                st.write(f"{instruction['project']} - {instruction['villa']}")
            with cols_row[3]:
                client_display = instruction['client_name'][:25] + "..." if len(instruction['client_name']) > 25 else instruction['client_name']
                st.write(client_display)
            with cols_row[4]:
                st.write(instruction['payment_order'])
            with cols_row[5]:
                st.write(f"€{instruction['amount']}")
            with cols_row[6]:
                if st.button("📥", key=f"load_pi_{actual_idx}", help="Load this payment instruction"):
                    st.session_state.selected_payment_instruction = instruction
                    st.session_state.load_into_form = True   # flag to prefill widgets
                    st.rerun()
            with cols_row[7]:
                if st.button("🗑️", key=f"delete_pi_{actual_idx}", help="Delete this payment instruction"):
                    st.session_state.payment_instructions_db.pop(actual_idx)
                    st.success("Payment instruction deleted!")
                    st.rerun()
        st.markdown("---")

    # ---------- Defaults & auto-fill after load ----------
    _ensure_form_state_defaults()

    selected_instruction = st.session_state.get('selected_payment_instruction')
    if st.session_state.get('load_into_form') and selected_instruction:
        _load_into_form_from_instruction(selected_instruction)
        st.session_state.load_into_form = False
        st.markdown('<div class="success-msg">✅ Payment instruction loaded! Fields filled automatically.</div>', unsafe_allow_html=True)
    elif 'last_payment' in st.session_state and not any(st.session_state.get(k) for k in ['selected_payment_instruction','load_into_form']):
        # Optional hint if nothing loaded but there is a recent payment
        st.markdown('<div class="info-msg">📌 Recent payment instruction detected! You can load it from history above.</div>', unsafe_allow_html=True)

    # ---------- Form UI ----------
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("### 📝 Receipt of Funds Details")

        # Project select (value from state)
        st.selectbox(
            "Project",
            _all_projects(),
            key="receipt_project"
        )

        # Sync villa options for current project
        villa_options_receipt = _villas_for(st.session_state.receipt_project)
        if st.session_state.receipt_villa not in villa_options_receipt:
            st.session_state.receipt_villa = villa_options_receipt[0]

        st.selectbox(
            "Villa",
            villa_options_receipt,
            key="receipt_villa"
        )

        receipt_client = VILLA_OWNERS.get((st.session_state.receipt_project, st.session_state.receipt_villa), "")
        if receipt_client:
            st.markdown(f'<div class="info-msg">👤 <strong>Client:</strong> {receipt_client}</div>', unsafe_allow_html=True)

        st.text_input("Payment Order Number", placeholder="001", key="receipt_payment_order")
        st.text_input("Amount (€)", placeholder="5000", key="receipt_amount")
        st.date_input("Date of Receipt", key="receipt_date")
        st.text_area(
            "Extra Receipt Text (Optional)",
            placeholder="Additional information about the payment...",
            help="This text will appear in the receipt. Leave empty if not needed.",
            key="receipt_extra_text"
        )

        # Clear form really clears everything
        if st.button("🔄 Clear Form", use_container_width=True, key="clear_receipt_form"):
            _clear_form()
            st.rerun()

    with col2:
        st.markdown("### 📊 Receipt Preview")
        if st.session_state.receipt_payment_order and st.session_state.receipt_amount:
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 2px solid #e0e0e0; text-align: left;">
                <h4 style="color: #1e3c72; margin-bottom: 1rem;">🧾 Receipt of Funds Preview</h4>
                <p><strong>To:</strong> {receipt_client}</p>
                <p><strong>Project:</strong> {st.session_state.receipt_project}</p>
                <p><strong>Villa #:</strong> {st.session_state.receipt_villa}</p>
                <p><strong>Payment Order:</strong> {st.session_state.receipt_payment_order}</p>
                <p><strong>Date:</strong> {st.session_state.receipt_date.strftime('%d/%m/%Y')}</p>
                <p><strong>Amount:</strong> <span style="font-weight: bold;">€{st.session_state.receipt_amount}</span></p>
                {f'<p><strong>Extra Text:</strong> {st.session_state.receipt_extra_text[:50]}{"..." if len(st.session_state.receipt_extra_text) > 50 else ""}</p>' if st.session_state.receipt_extra_text else ""}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; border: 2px dashed #dee2e6; text-align: center;">
                <h4 style="color: #6c757d;">📄 Receipt Preview</h4>
                <p style="color: #6c757d;">Fill in the details to see preview</p>
            </div>
            """, unsafe_allow_html=True)

    # ---------- Generate DOCX from template ----------
    if st.button("📥 Generate and Download Receipt of Funds", use_container_width=True, key="generate_receipt"):
        rp = st.session_state.receipt_project
        rv = st.session_state.receipt_villa
        rc = VILLA_OWNERS.get((rp, rv), "")
        rpo = st.session_state.receipt_payment_order
        ra = st.session_state.receipt_amount
        rd = st.session_state.receipt_date
        rx = st.session_state.receipt_extra_text

        if rpo and ra:
            try:
                template_path = _find_template_path()
                if not template_path:
                    raise FileNotFoundError("Template file 'Receipt_of_Funds.docx' not found. Place it in the app folder or /mnt/data.")
                
                mapping = {
                    "{{client_name}}": rc or "",
                    "{{plot}}": rp or "",
                    "{{villa_no}}": rv or "",
                    "{{payment_order_number}}": rpo or "",
                    "{{sum}}": str(ra or ""),
                    "{{date}}": rd.strftime("%d/%m/%Y") if rd else "",
                    "{{Extra Receipt text}}": (rx if rx and rx.strip() else "")
                }

                doc = _fill_template_docx(template_path, mapping)
                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)

                # filename with two spaces before client_name (as requested)
                filename = f"{rp} - Receipt of Funds {rpo} -  {rc}.docx"

                # Save a record so TAB 4 shows it
                receipt_record = {
                    "type": "Receipt of Funds",
                    "number": rpo,
                    "date": rd.strftime("%Y-%m-%d"),
                    "project": rp,
                    "villa": rv,
                    "client": rc,
                    "amount": ra,
                    "notes": rx,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                st.session_state.receipts_db.append(receipt_record)

                st.markdown('<div class="success-msg">✅ Receipt of Funds generated successfully!</div>', unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download Receipt of Funds (DOCX)",
                    data=buffer,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

            except FileNotFoundError as e:
                st.error(f"❌ {str(e)}")
            except Exception as e:
                st.error(f"❌ Error generating receipt: {str(e)}")
        else:
            st.warning("⚠️ Please fill in Payment Order Number and Amount")
    
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
        # חישוב סכום כולל באופן חסין גם למחרוזות
        total_amount = 0.0
        for r in all_records:
            try:
                amt = float(str(r.get('amount', '')).replace(',', '').strip())
                total_amount += amt
            except Exception:
                pass
        unique_projects = len(set(r.get('project', '') for r in all_records if r.get('project')))

        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-value">{total_records}</div>
                <div class="metric-label">Total Records</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">€{total_amount:,.2f}</div>
                <div class="metric-label">Total Amount</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{unique_projects}</div>
                <div class="metric-label">Projects</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_project = st.selectbox(
                "Filter by Project",
                ["All"] + sorted(set(r.get('project', '') for r in all_records if r.get('project'))),
                key="filter_project"
            )
        with col2:
            filter_villa = st.selectbox(
                "Filter by Villa",
                ["All"] + sorted(set(r.get('villa', '') for r in all_records if r.get('villa'))),
                key="filter_villa"
            )
        with col3:
            # ⬅️ הוספתי Receipt of Funds
            filter_type = st.selectbox(
                "Filter by Type",
                ["All", "Invoice", "Receipt of Funds", "Payment Instruction"],
                key="filter_type"
            )
        
        # Apply filters
        filtered_records = all_records
        if filter_project != "All":
            filtered_records = [r for r in filtered_records if r.get('project') == filter_project]
        if filter_villa != "All":
            filtered_records = [r for r in filtered_records if r.get('villa') == filter_villa]
        if filter_type != "All":
            filtered_records = [r for r in filtered_records if r.get('type') == filter_type]
        
        # Display table
        if filtered_records:
            st.markdown("### 📊 Records Table")

            for idx, record in enumerate(filtered_records):
                # תצוגה חסינה לשדות חסרים
                display_type = record.get('type', '')
                display_number = record.get('number') or record.get('payment_order') or record.get('invoice_number') or "N/A"
                display_project = record.get('project', '')
                display_villa = record.get('villa', '')
                display_amount = record.get('amount', '')
                with st.expander(f"{display_type} #{display_number} - {display_project} {display_villa} - €{display_amount}"):
                    colA, colB = st.columns([3, 1])
                    with colA:
                        st.write(f"**Date:** {record.get('date', '')}")
                        st.write(f"**Client:** {record.get('client', '')}")
                        st.write(f"**Amount:** €{display_amount}")
                        notes_val = record.get('notes') or record.get('extra_text') or ""
                        if notes_val:
                            st.write(f"**Notes:** {notes_val}")
                    with colB:
                        # מחיקה בטוחה מתוך הרשימה המקורית לפי זהות האובייקט
                        if st.button("🗑️ Delete", key=f"delete_{idx}"):
                            for i, r0 in enumerate(st.session_state.receipts_db):
                                if r0 is record:
                                    st.session_state.receipts_db.pop(i)
                                    break
                            st.rerun()
        else:
            st.info("No records found with the selected filters.")
        
        # Export options
        st.markdown("---")
        st.markdown("### 📥 Export Options")
        
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
