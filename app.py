import streamlit as st
import pandas as pd
import re
import datetime
from io import BytesIO

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
def process_athens_file(df):
    df = df.copy()
    # Fix for date formatting issue
    df['Ημερομηνία'] = pd.to_datetime(df['Ημερομηνία'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Περιγραφή'])
    results = []

    for _, row in df.iterrows():
        original_desc = str(row['Περιγραφή'])
        desc = original_desc.upper()
        amount = abs(float(str(row['Ποσό συναλλαγής']).replace('.', '').replace(',', '.')))

        entry = {
            "Date": row['Ημερομηνία'].strftime('%d/%m/%Y') if not pd.isnull(row['Ημερομηνία']) else '',
            "Income/outcome": "Income" if row['Ποσό συναλλαγής'] > 0 else "Outcome",
            "Plot": "Diakofti" if "DIAKOFTI" in desc else ("Mobee" if "MOBEE" in desc else "All Projects"),
            "Expenses Type": "Soft Cost",
            "Type": "",
            "Supplier": "",
            "Description": desc,
            "In": amount if row['Ποσό συναλλαγής'] > 0 else "",
            "Out": -amount if row['Ποσό συναλλαγής'] < 0 else "",
            "Total": amount if row['Ποσό συναλλαγής'] > 0 else -amount,
            "Progressive Ledger Balance": "",
            "Payment details": "",
            "Original Description": original_desc
        }

        filled = False

        # Rule: Detect bank fee entries by keywords and small amounts
        if any(word in desc for word in ["DINNER", "FOOD", "CAFE", "COFFEE", "LUNCH", "BREAKFAST", "ΦΑΓΗΤΟ", "ΕΣΤΙΑΤΟΡΙΟ", "ΚΑΦΕ"]):
            entry["Type"] = "F&B"
            entry["Supplier"] = "General"
            entry["Description"] = "F&B"
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
            entry["Plot"] = "Lefkes"
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

        if "AEGEANWEB" in desc:
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
    # Move Original Description column to the end for export
    if 'Original Description' in result_df.columns:
        original_col = result_df.pop('Original Description')
        result_df.insert(len(result_df.columns), 'Original Description', original_col)
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
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; font-size: 0.9rem;">
                <p><strong>Format Guide</strong></p>
                <ul style="padding-left: 1rem; margin-bottom: 0;">
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
        <h2 class="card-title">Receipt Generator <span class="coming-soon">Coming Soon</span></h2>
        <p>Generate professional receipts from your transaction data.</p>
        
        <div style="display: flex; align-items: center; justify-content: center; padding: 2rem;">
            <div style="text-align: center;">
                <img src="https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG" width="120">
                <p style="margin-top: 1rem; color: #666; font-size: 0.9rem;">
                    We're developing this feature to help you create and manage receipts with ease.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- PAYMENT INSTRUCTIONS PAGE ---
elif selected_page == "Payment Instructions":
    st.markdown("""
    <div class="card">
        <h2 class="card-title">Payment Instructions <span class="coming-soon">Coming Soon</span></h2>
        <p>Create and track payment instructions for vendors and contractors.</p>
        
        <div style="display: flex; align-items: center; justify-content: center; padding: 2rem;">
            <div style="text-align: center;">
                <img src="https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG" width="120">
                <p style="margin-top: 1rem; color: #666; font-size: 0.9rem;">
                    This feature will help you manage payment schedules and instructions efficiently.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer">
    Aiolos Financial Tools © 2025 • Build 1.2.1
</div>
""", unsafe_allow_html=True)
