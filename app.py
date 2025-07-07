import streamlit as st
import pandas as pd
import re
import datetime
from io import BytesIO
from docx import Document

# --- UI CONFIG ---
st.set_page_config(
    page_title="Aiolos Financial Tools",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define pages
PAGES = {
    "Excel Classifier": "classifier",
    "Receipt Generator": "receipts",
    "Payment Instructions": "payments"
}

# --- PLOTS RECOGNITION FUNCTIONS ---
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

# --- PROCESSING FUNCTIONS ---
# --- PROCESSING FUNCTIONS ---
def process_athens_file(df):
    df = df.copy()
    # Fix for date formatting issue
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
            "Location": "Diakofti" if "DIAKOFTI" in desc else ("Mobee" if "MOBEE" in desc else "All Projects"),
            "Project": "Diakofti" if "DIAKOFTI" in desc else ("Mobee" if "MOBEE" in desc else "All Projects"),
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

        # Rule: Detect bank fee entries by keywords and small amounts
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

        if not filled:
            entry["Description"] = f"🟨 {entry['Description']}"

        results.append(entry)

    result_df = pd.DataFrame(results)
    
    # Define the order of columns to match the image
    column_order = [
        "Date", 
        "Income/Outcome", 
        "Expenses Type", 
        "Location", 
        "Project", 
        "Supplier", 
        "Type", 
        "Description", 
        "Income", 
        "Outcome", 
        "Total", 
        "Balance", 
        "Repayment",
        "Original Description"
    ]
    
    # Reorder the columns for the final output
    result_df = result_df[column_order]
    
    return result_df
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

# --- CUSTOM CSS FOR CLEAN, MINIMAL UI ---
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #0366d6;
        --background: #ffffff;
        --card-bg: #ffffff;
        --text: #333333;
        --border: #eaeaea;
        --accent: #f3f5f7;
        --success: #28a745;
        --warning: #ffc107;
        --radius: 8px;
    }
    
    /* Base typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: var(--text);
    }
    
    /* App header */
    .app-header {
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border);
    }
    
    .app-title {
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: 0.25rem;
        color: var(--text);
    }
    
    .app-subtitle {
        font-weight: 400;
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 1rem;
    }
    
    /* Card styling */
    .card {
        background-color: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .card-title {
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 1rem;
        color: var(--text);
    }
    
    /* Status indicators */
    .status {
        padding: 0.75rem;
        border-radius: var(--radius);
        margin: 1rem 0;
    }
    
    .status-success {
        background-color: rgba(40, 167, 69, 0.1);
        border-left: 3px solid var(--success);
    }
    
    .status-warning {
        background-color: rgba(255, 193, 7, 0.1);
        border-left: 3px solid var(--warning);
    }
    
    /* Progress steps */
    .steps {
        display: flex;
        margin: 1rem 0;
        padding: 0;
        list-style: none;
    }
    
    .step-item {
        flex: 1;
        text-align: center;
        padding: 0.5rem;
        font-size: 0.8rem;
        position: relative;
        color: #999;
    }
    
    .step-active {
        color: var(--primary);
        font-weight: 500;
    }
    
    .step-complete {
        color: var(--success);
    }
    
    .step-item:not(:last-child):after {
        content: '';
        position: absolute;
        top: 50%;
        right: -0.5rem;
        width: 1rem;
        height: 1px;
        background-color: var(--border);
    }
    
    /* Coming soon tag */
    .coming-soon {
        display: inline-block;
        background-color: var(--accent);
        padding: 0.2rem 0.5rem;
        border-radius: var(--radius);
        font-size: 0.7rem;
        margin-left: 0.5rem;
        font-weight: 500;
        color: #777;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        color: #777;
        font-size: 0.8rem;
        border-top: 1px solid var(--border);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Button styling */
    .stButton>button {
        background-color: var(--primary);
        color: white;
        font-weight: 500;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: var(--radius);
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: rgba(3, 102, 214, 0.8);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background-color: var(--accent);
        padding: 0.75rem 1rem;
        border-radius: var(--radius);
        flex: 1;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text);
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #666;
    }
    
    /* File uploader */
    .uploadedFile {
        border: 1px dashed var(--border);
        border-radius: var(--radius);
        padding: 1rem;
        background-color: var(--accent);
    }
    
    /* Data preview */
    .preview-container {
        margin: 1rem 0;
        border: 1px solid var(--border);
        border-radius: var(--radius);
        overflow: hidden;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: var(--accent);
    }
    
    /* Form elements styling */
    .form-group {
        margin-bottom: 1.2rem;
    }
    
    .form-label {
        font-weight: 500;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* Info panel */
    .info-panel {
        background-color: #f8f9fa; 
        padding: 1.25rem; 
        border-radius: 8px;
        font-size: 0.9rem; 
        height: 100%; 
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .info-panel-title {
        font-weight: 500; 
        margin-top: 0;
        margin-bottom: 0.5rem;
    }
    
    .info-panel ul {
        padding-left: 1.2rem; 
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="app-header">
    <h1 class="app-title">Aiolos Financial Tools</h1>
    <p class="app-subtitle">Financial management simplified</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image('https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG', width=80)
    
    selected_page = st.radio(
        "",
        list(PAGES.keys())
    )
    
    st.markdown("---")
    st.markdown("""
        <div style="font-size: 0.85rem; color: #666;">
        Aiolos Financial Tools • v1.2.1<br>
        Streamline your financial processes
        </div>
    """, unsafe_allow_html=True)

# --- EXCEL CLASSIFIER PAGE ---
if selected_page == "Excel Classifier":
    st.markdown("""
    <div class="card">
        <h2 class="card-title">Excel Classifier</h2>
        <p>Categorize and organize your financial Excel statements with ease.</p>
    """, unsafe_allow_html=True)
    
    # Track progress
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    # Progress steps
    st.markdown("""
        <ul class="steps">
            <li class="step-item {0}">Select Format</li>
            <li class="step-item {1}">Upload File</li>
            <li class="step-item {2}">Process Data</li>
            <li class="step-item {3}">Download Results</li>
        </ul>
    """.format(
        "step-active" if st.session_state.step == 1 else "step-complete" if st.session_state.step > 1 else "",
        "step-active" if st.session_state.step == 2 else "step-complete" if st.session_state.step > 2 else "",
        "step-active" if st.session_state.step == 3 else "step-complete" if st.session_state.step > 3 else "",
        "step-active" if st.session_state.step == 4 else "step-complete" if st.session_state.step > 4 else ""
    ), unsafe_allow_html=True)
    
    # Form layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Format selection
        project_type = st.selectbox(
            "Format Type",
            ["DIAKOFTI", "ATHENS"],
            index=0,
            help="Select the format that matches your data structure"
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Excel File",
            type=["xlsx", "csv"],
            help="Upload an Excel or CSV file to process"
        )
    
    with col2:
        st.markdown("""
            <div class="info-panel">
                <p class="info-panel-title">Format Guide</p>
                <ul>
                    <li>DIAKOFTI: For plot-based transactions</li>
                    <li>ATHENS: For Athens office transactions</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # Processing section
    if uploaded_file:
        st.session_state.step = 2
        
        st.markdown("""
        <div class="status status-success">
            <strong>File uploaded:</strong> {0}<br>
            <strong>Format:</strong> {1}
        </div>
        """.format(uploaded_file.name, project_type), unsafe_allow_html=True)
        
        # Process button
        process_button = st.button("Process File")
        
        if process_button:
            with st.spinner("Processing data..."):
                if project_type == "DIAKOFTI":
                    if uploaded_file.name.endswith(".csv"):
                        raw_df = pd.read_csv(uploaded_file, encoding="ISO-8859-7")
                    else:
                        raw_df = pd.read_excel(uploaded_file)
                    
                    result_df = process_file(raw_df)
                    st.session_state.step = 3
                    
                elif project_type == "ATHENS":
                    raw_df = pd.read_excel(uploaded_file)
                    result_df = process_athens_file(raw_df)
                    st.session_state.step = 3
                
                # Store results
                st.session_state.result_df = result_df
    
    # Results display
    if 'result_df' in st.session_state:
        result_df = st.session_state.result_df
        
        # Summary metrics
        marked_entries = result_df['Description'].str.contains('🟨').sum()
        auto_classified = len(result_df) - marked_entries
        percentage = (auto_classified / len(result_df)) * 100 if len(result_df) > 0 else 0
        
        st.markdown("""
        <div class="card">
            <h3 class="card-title">Results Summary</h3>
            <div class="metric-row">
                <div class="metric-card">
                    <div class="metric-value">{0}</div>
                    <div class="metric-label">Total Entries</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{1}</div>
                    <div class="metric-label">Entries Needing Review</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{2:.1f}%</div>
                    <div class="metric-label">Auto-Classification Rate</div>
                </div>
            </div>
        """.format(len(result_df), marked_entries, percentage), unsafe_allow_html=True)
        
        # Preview section
        st.markdown("""
            <h3 class="card-title">Data Preview</h3>
            <div class="preview-container">
        """, unsafe_allow_html=True)
        st.dataframe(result_df.head(5), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Download section
        to_download = BytesIO()
        result_df.to_excel(to_download, index=False, engine='openpyxl')
        
        st.download_button(
            label="Download Processed File",
            data=to_download.getvalue(),
            file_name=f"{project_type.lower()}_processed_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.session_state.step = 4
        st.markdown("""
            <div class="status status-success">
                <strong>✓ Processing complete!</strong> Your file is ready to download.
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- RECEIPT GENERATOR PAGE ---
elif selected_page == "Receipt Generator":
    st.markdown("""
    <div class="card">
        <h2 class="card-title">Receipt Generator</h2>
        <p>Generate professional payment receipts for villa owners.</p>
    """, unsafe_allow_html=True)

    # Villa owners data
    villa_owners = {
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

    # Track receipt generation state
    if 'receipt_step' not in st.session_state:
        st.session_state.receipt_step = 1
    
    # Show steps
    st.markdown("""
        <ul class="steps">
            <li class="step-item {0}">Select Villa</li>
            <li class="step-item {1}">Payment Details</li>
            <li class="step-item {2}">Generate Receipt</li>
        </ul>
    """.format(
        "step-active" if st.session_state.receipt_step == 1 else "step-complete" if st.session_state.receipt_step > 1 else "",
        "step-active" if st.session_state.receipt_step == 2 else "step-complete" if st.session_state.receipt_step > 2 else "",
        "step-active" if st.session_state.receipt_step == 3 else "step-complete" if st.session_state.receipt_step > 3 else ""
    ), unsafe_allow_html=True)
    
    # Main form layout in columns for better arrangement
    col1, col2 = st.columns([3, 2])
    
    with col1:
        with st.form("receipt_form"):
            # Villa selection section
            st.markdown("<p style='font-weight: 500; margin-bottom: 0.5rem;'>Villa Information</p>", unsafe_allow_html=True)
            project = st.selectbox(
                "Select Project", 
                sorted(set(k[0] for k in villa_owners)),
                help="Choose the project plot"
            )
            
            villa_options = sorted(set(k[1] for k in villa_owners if k[0] == project))
            villa = st.selectbox(
                "Select Villa", 
                villa_options,
                help="Select the villa number"
            )
            
            client_name = villa_owners.get((project, villa), "")
            if client_name:
                st.markdown(f"""
                <div style="background-color: var(--accent); padding: 0.75rem; border-radius: var(--radius); font-size: 0.9rem;">
                    <strong>Owner:</strong> {client_name}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<p style='font-weight: 500; margin-top: 1.5rem;'>Payment Details</p>", unsafe_allow_html=True)
            payment_order_number = st.text_input("Payment Order Number")
            sum_euro = st.text_input("Sum in Euro (€)")
            extra_text = st.text_area("Extra Payment Text (optional)", "")
            generate_button = st.form_submit_button("Generate Receipt")

    with col2:
        st.markdown("""
        <div class="info-panel">
            <p class="info-panel-title">Instructions</p>
            <ul>
                <li>Select the villa to auto-fill owner name</li>
                <li>Enter payment number and amount</li>
                <li>Click to generate a ready-to-send Word document</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    if generate_button:
        st.session_state.receipt_step = 3
        template = Document("default_tempate.docx")

        for p in template.paragraphs:
            p.text = p.text.replace("{{date}}", datetime.datetime.now().strftime("%d/%m/%Y"))
            p.text = p.text.replace("{{plot}}", project)
            p.text = p.text.replace("{{villa_no}}", villa)
            p.text = p.text.replace("{{client_name}}", client_name)
            p.text = p.text.replace("{{payment_order_number}}", payment_order_number)
            p.text = p.text.replace("{{sum}}", sum_euro)
            p.text = p.text.replace("{{Extra Payment text}}", extra_text)

        buffer = BytesIO()
        template.save(buffer)
        buffer.seek(0)

        filename = f"Diakofti Village Project - {project} {villa} - Payment order #{payment_order_number}.docx"

        st.markdown("""
        <div class="status status-success">
            <strong>✓ Receipt ready!</strong> Download your completed file below.
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            label="Download Word Receipt",
            data=buffer,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    st.markdown("</div>", unsafe_allow_html=True)
