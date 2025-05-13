import streamlit as st
import pandas as pd
import re
import datetime
from io import BytesIO

# --- UI CONFIG ---
st.set_page_config(
    page_title="Aiolos Excel Classifier",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS FOR ENHANCED UI ---
st.markdown("""
    <style>
        /* Global styling */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        body {
            font-family: 'Poppins', sans-serif;
            color: #333;
        }
        
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #eef2f7 100%);
        }
        
        /* Header styling */
        .header-container {
            background-color: #003366;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            align-items: center;
            background-image: linear-gradient(135deg, #003366 0%, #005599 100%);
        }
        
        .app-header {
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        
        .app-subheader {
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.1rem;
            font-weight: 400;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        /* Card styling */
        .card {
            background-color: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        
        .card-title {
            color: #003366;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            border-bottom: 2px solid #eef2f7;
            padding-bottom: 0.75rem;
        }
        
        /* Button styling */
        .custom-button {
            background: linear-gradient(135deg, #003366 0%, #005599 100%);
            color: white;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .custom-button:hover {
            background: linear-gradient(135deg, #004080 0%, #0066b3 100%);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #003366 0%, #005599 100%);
            color: white;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .stButton>button:hover {
            background: linear-gradient(135deg, #004080 0%, #0066b3 100%);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }
        
        /* Logo styling */
        .logo-container {
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
        }
        
        .logo {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* File uploader styling */
        .uploadedFile {
            background-color: #f0f5ff;
            border-radius: 8px;
            border: 2px dashed #003366;
            padding: 1.5rem;
            text-align: center;
            margin-top: 1rem;
        }
        
        /* Status indicator styling */
        .status-success {
            background-color: #e6f7e6;
            color: #00701a;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #00701a;
            margin-top: 1.5rem;
        }
        
        .status-waiting {
            background-color: #fff8e6;
            color: #8a6d00;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            margin-top: 1.5rem;
        }
        
        /* Project selection styling */
        .select-container {
            background-color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Animation keyframes */
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            color: #777;
            font-size: 0.8rem;
        }
        
        /* Divider styling */
        .divider {
            margin: 2rem 0;
            height: 1px;
            background: linear-gradient(90deg, rgba(0,51,102,0) 0%, rgba(0,51,102,0.3) 50%, rgba(0,51,102,0) 100%);
        }
        
        /* Progress indicator */
        .progress-indicator {
            display: flex;
            justify-content: space-between;
            margin: 2rem 0;
        }
        
        .step {
            flex: 1;
            text-align: center;
            padding: 1rem 0;
            position: relative;
        }
        
        .step-active {
            font-weight: 600;
            color: #003366;
        }
        
        .step-complete {
            color: #007bff;
        }
        
        .step-pending {
            color: #aaa;
        }
        
        .step-circle {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background-color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.5rem;
            border: 2px solid #ddd;
            font-weight: 600;
        }
        
        .step-circle-active {
            border-color: #003366;
            background-color: #003366;
            color: white;
        }
        
        .step-circle-complete {
            border-color: #007bff;
            background-color: #007bff;
            color: white;
        }
        
        /* Selectbox styling */
        div[data-baseweb="select"] > div {
            background-color: white;
            border-radius: 8px;
            border: 1px solid #eaeaea;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# --- APP HEADER ---
st.markdown("""
    <div class="header-container fade-in">
        <div class="logo-container">
            <img src='https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG' alt='Aiolos Logo' class="logo">
        </div>
        <h1 class="app-header">Aiolos Excel Classifier</h1>
        <p class="app-subheader">Streamline your financial statements processing with AI-powered categorization</p>
    </div>
""", unsafe_allow_html=True)

# --- MAIN CONTENT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="card-title">📊 Upload & Process</h2>', unsafe_allow_html=True)
    
    # Progress indicator
    step = 1
    if 'step' in st.session_state:
        step = st.session_state.step
    
    st.markdown(f"""
        <div class="progress-indicator">
            <div class="step {'step-active' if step == 1 else 'step-complete' if step > 1 else 'step-pending'}">
                <div class="step-circle {'step-circle-active' if step == 1 else 'step-circle-complete' if step > 1 else ''}">1</div>
                <div>Select Format</div>
            </div>
            <div class="step {'step-active' if step == 2 else 'step-complete' if step > 2 else 'step-pending'}">
                <div class="step-circle {'step-circle-active' if step == 2 else 'step-circle-complete' if step > 2 else ''}">2</div>
                <div>Upload File</div>
            </div>
            <div class="step {'step-active' if step == 3 else 'step-complete' if step > 3 else 'step-pending'}">
                <div class="step-circle {'step-circle-active' if step == 3 else 'step-circle-complete' if step > 3 else ''}">3</div>
                <div>Process Data</div>
            </div>
            <div class="step {'step-active' if step == 4 else 'step-complete' if step > 4 else 'step-pending'}">
                <div class="step-circle {'step-circle-active' if step == 4 else 'step-circle-complete' if step > 4 else ''}">4</div>
                <div>Download Result</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Format selection
    st.markdown("<p><strong>Step 1:</strong> Select your Excel format type below:</p>", unsafe_allow_html=True)
    st.markdown('<div class="select-container">', unsafe_allow_html=True)
    project_type = st.selectbox(
        "Choose Excel Format:",
        ["DIAKOFTI", "ATHENS"],
        index=0,
        help="Select the appropriate format based on your Excel file structure"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File upload
    st.markdown("<p><strong>Step 2:</strong> Upload your financial Excel file:</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop your Excel file here",
        type=["xlsx", "csv"],
        help="Upload your financial statements Excel file (.xlsx or .csv format)"
    )
    
    if uploaded_file:
        st.session_state.step = 2
        file_details = {"Filename": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": f"{uploaded_file.size / 1024:.2f} KB"}
        
        st.markdown('<div class="status-success">', unsafe_allow_html=True)
        st.write(f"✅ File uploaded successfully!")
        st.write(f"📄 **File name:** {file_details['Filename']}")
        st.write(f"📊 **Format type:** {project_type}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="card-title">ℹ️ About This Tool</h2>', unsafe_allow_html=True)
    st.markdown("""
        This application helps you categorize and organize your financial Excel statements automatically.
        
        **Key Features:**
        - Supports multiple Excel formats (DIAKOFTI, ATHENS)
        - Automatic transaction categorization
        - Plot identification and assignment
        - Expense type classification
        - Ready-to-use output file
        
        **How to use:**
        1. Select your Excel format
        2. Upload your file
        3. Process the data
        4. Download the categorized file
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="card-title">🔍 Processing Details</h2>', unsafe_allow_html=True)
    
    if project_type == "DIAKOFTI":
        st.markdown("""
            **DIAKOFTI Format Processing:**
            
            The system will identify:
            - Plot names (Y1, Y2, Y3, etc.)
            - Transaction types (Accounting, Marketing, etc.)
            - Suppliers and payment details
            - Income vs. outcome transactions
            
            Transactions requiring manual review will be marked with 🟨
        """)
    else:
        st.markdown("""
            **ATHENS Format Processing:**
            
            The system will identify:
            - Project allocations (Diakofti, Mobee, All Projects)
            - Transaction types (F&B, Transportation, etc.)
            - Supplier details
            - Income vs. outcome transactions
            
            Transactions requiring manual review will be marked with 🟨
        """)
    st.markdown('</div>', unsafe_allow_html=True)

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

# --- PROCESSING AND RESULTS SECTION ---
if uploaded_file:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="card-title">🔄 Processing Results</h2>', unsafe_allow_html=True)
    
    # Processing animation
    with st.spinner("Processing your file... This may take a moment."):
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
    
    # Display processing summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entries", f"{len(result_df)}")
    with col2:
        # Count marked entries
        marked_entries = result_df['Description'].str.contains('🟨').sum()
        st.metric("Entries Needing Review", f"{marked_entries}")
    with col3:
        auto_classified = len(result_df) - marked_entries
        percentage = (auto_classified / len(result_df)) * 100 if len(result_df) > 0 else 0
        st.metric("Auto-Classified Rate", f"{percentage:.1f}%")
    
    # Preview results
    st.subheader("Preview Results")
    st.dataframe(result_df.head(5), use_container_width=True)
    
    # Download button
    to_download = BytesIO()
    result_df.to_excel(to_download, index=False, engine='openpyxl')
    
    st.download_button(
        label="Download Processed File",
        data=to_download.getvalue(),
        file_name=f"{project_type.lower()}_processed_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Click to download the fully processed Excel file"
    )
    
    st.session_state.step = 4
    st.markdown('<div class="status-success">', unsafe_allow_html=True)
    st.write("✅ Processing complete! Click the button above to download your file.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
    <div class="footer">
        <p>Aiolos Excel Classifier &copy; 2025 | All Rights Reserved</p>
    </div>
""", unsafe_allow_html=True)
