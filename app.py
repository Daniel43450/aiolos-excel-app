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

# --- CUSTOM CSS FOR MINIMALIST UI ---
st.markdown("""
    <style>
        /* Global styling */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        body {
            font-family: 'Inter', sans-serif;
            color: #333;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #f8f9fa;
        }
        
        /* Header styling */
        .header-container {
            padding: 1.5rem 0;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid #eaeaea;
        }
        
        .app-header {
            color: #1a1a1a;
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        
        .app-subheader {
            color: #777;
            font-size: 1rem;
            font-weight: 400;
        }
        
        /* Card styling */
        .card {
            background-color: white;
            border-radius: 4px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid #eaeaea;
        }
        
        .card-title {
            color: #1a1a1a;
            font-size: 1.2rem;
            font-weight: 500;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #eaeaea;
        }
        
        /* Button styling - more minimalist */
        .stButton>button {
            background-color: #1a1a1a;
            color: white;
            border-radius: 4px;
            font-weight: 500;
            border: none;
            padding: 0.5rem 1rem;
        }
        
        .stButton>button:hover {
            background-color: #333;
        }
        
        /* File uploader styling */
        .uploadedFile {
            border: 1px solid #eaeaea;
            border-radius: 4px;
            padding: 1rem;
        }
        
        /* Status indicator styling */
        .status-success {
            background-color: #f2f9f2;
            color: #2e7d32;
            padding: 0.75rem;
            border-radius: 4px;
            border-left: 3px solid #2e7d32;
            margin-top: 1rem;
        }
        
        .status-waiting {
            background-color: #fff8e6;
            color: #856404;
            padding: 0.75rem;
            border-radius: 4px;
            border-left: 3px solid #ffc107;
            margin-top: 1rem;
        }
        
        /* Progress indicator */
        .step-indicator {
            display: flex;
            margin: 1.5rem 0;
            gap: 0.5rem;
        }
        
        .step {
            background-color: #f0f0f0;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 0.9rem;
            color: #777;
        }
        
        .step-active {
            background-color: #1a1a1a;
            color: white;
        }
        
        .step-complete {
            background-color: #eaf0ea;
            color: #2e7d32;
        }
        
        /* Coming soon label */
        .coming-soon {
            display: inline-block;
            background-color: #f0f0f0;
            color: #777;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            margin-left: 0.5rem;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            color: #777;
            font-size: 0.8rem;
            border-top: 1px solid #eaeaea;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image('https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG', width=100)
    st.title("Aiolos Financial Tools")
    
    selected_page = st.radio(
        "Navigation",
        list(PAGES.keys())
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
        This application helps you manage and organize financial data for Aiolos projects.
    """)

# --- APP HEADER ---
st.markdown("""
    <div class="header-container">
        <h1 class="app-header">Aiolos Financial Tools</h1>
        <p class="app-subheader">Streamline your financial management processes</p>
    </div>
""", unsafe_allow_html=True)

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

# --- PAGE CONTENT BASED ON SELECTION ---
if selected_page == "Excel Classifier":
    st.subheader("Excel Classifier")
    st.markdown("Categorize and organize your financial Excel statements automatically.")
    
    # Create two columns
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="card-title">Upload & Process</h3>', unsafe_allow_html=True)
        
        # Step indicator
        step = 1
        if 'step' in st.session_state:
            step = st.session_state.step
        
        st.markdown(f"""
            <div class="step-indicator">
                <div class="step {'step-active' if step == 1 else 'step-complete' if step > 1 else ''}">1. Select Format</div>
                <div class="step {'step-active' if step == 2 else 'step-complete' if step > 2 else ''}">2. Upload File</div>
                <div class="step {'step-active' if step == 3 else 'step-complete' if step > 3 else ''}">3. Process Data</div>
                <div class="step {'step-active' if step == 4 else 'step-complete' if step > 4 else ''}">4. Download Result</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Format selection
        project_type = st.selectbox(
            "Excel Format:",
            ["DIAKOFTI", "ATHENS"],
            index=0,
            help="Select the appropriate format based on your Excel file structure"
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Excel file",
            type=["xlsx", "csv"],
            help="Upload your financial statements Excel file (.xlsx or .csv format)"
        )
        
        if uploaded_file:
            st.session_state.step = 2
            st.markdown('<div class="status-success">', unsafe_allow_html=True)
            st.write(f"✅ File uploaded: {uploaded_file.name}")
            st.write(f"📊 Format type: {project_type}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="card-title">Format Details</h3>', unsafe_allow_html=True)
        
        if project_type == "DIAKOFTI":
            st.markdown("""
                **DIAKOFTI Format**:
                
                - Plot identification
                - Transaction categorization
                - Supplier tracking
                - Payment details
            """)
        else:
            st.markdown("""
                **ATHENS Format**:
                
                - Project allocation
                - Transaction type  
                - Supplier details
                - Income/outcome tracking
            """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- PROCESSING AND RESULTS SECTION ---
    if uploaded_file:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="card-title">Processing Results</h3>', unsafe_allow_html=True)
        
        # Processing animation
        with st.spinner("Processing your file..."):
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
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.session_state.step = 4
        st.markdown('<div class="status-success">', unsafe_allow_html=True)
        st.write("✅ Processing complete!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "Receipt Generator":
    st.subheader("Receipt Generator")
    st.markdown('<span class="coming-soon">Coming Soon</span>', unsafe_allow_html=True)
    
    st.markdown("""
    This feature will allow you to:
    - Generate professional receipts from transaction data
    - Customize receipt templates
    - Add company logos and signatures
    - Export receipts in PDF format
    - Email receipts directly to clients
    
    We're working hard to make this available soon!
    """)
    
    # Mockup of the interface
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="card-title">Receipt Generator Interface</h3>', unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG", width=100)
    st.markdown("Preview of the receipt generator interface (coming soon)")
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "Payment Instructions":
    st.subheader("Payment Instructions")
    st.markdown('<span class="coming-soon">Coming Soon</span>', unsafe_allow_html=True)
    
    st.markdown("""
    This feature will allow you to:
    - Create payment instructions for vendors
    - Track payment status
    - Generate payment reports
    - Export payment details for accounting
    - Schedule recurring payments
    
    We're working hard to make this available soon!
    """)
    
    # Mockup of the interface
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="card-title">Payment Instructions Interface</h3>', unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG", width=100)
    st.markdown("Preview of the payment instructions interface (coming soon)")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        <p>Aiolos Financial Tools © 2025 | Version 1.2.0</p>
    </div>
""", unsafe_allow_html=True)
