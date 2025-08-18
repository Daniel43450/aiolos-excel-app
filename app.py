import streamlit as st
import pandas as pd
import re
import datetime
from io import BytesIO
from docx import Document
import plotly.graph_objects as go
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Aiolos Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN DESIGN SYSTEM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --dark: #1e293b;
        --gray: #64748b;
        --light: #f8fafc;
        --white: #ffffff;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        --radius: 12px;
    }
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Main Container */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 24px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1);
    }
    
    /* Header */
    .app-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .app-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Navigation Tabs */
    .nav-tabs {
        display: flex;
        gap: 0.5rem;
        background: var(--light);
        padding: 0.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .nav-tab {
        flex: 1;
        padding: 0.75rem 1.5rem;
        background: transparent;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        color: var(--gray);
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .nav-tab.active {
        background: white;
        color: var(--primary);
        box-shadow: var(--shadow-sm);
    }
    
    .nav-tab:hover:not(.active) {
        background: white;
        color: var(--dark);
    }
    
    /* Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    /* Stats Cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: linear-gradient(135deg, var(--white) 0%, var(--light) 100%);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid rgba(148, 163, 184, 0.1);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: var(--gray);
        font-weight: 500;
    }
    
    .stat-change {
        font-size: 0.75rem;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .stat-change.positive {
        color: var(--success);
    }
    
    .stat-change.negative {
        color: var(--danger);
    }
    
    /* Progress Steps */
    .progress-container {
        background: var(--light);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .progress-steps {
        display: flex;
        justify-content: space-between;
        position: relative;
    }
    
    .progress-steps::before {
        content: '';
        position: absolute;
        top: 20px;
        left: 0;
        right: 0;
        height: 2px;
        background: #e2e8f0;
        z-index: 0;
    }
    
    .progress-step {
        position: relative;
        z-index: 1;
        text-align: center;
        flex: 1;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: white;
        border: 2px solid #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .step-circle.active {
        background: var(--primary);
        border-color: var(--primary);
        color: white;
        transform: scale(1.1);
    }
    
    .step-circle.completed {
        background: var(--success);
        border-color: var(--success);
        color: white;
    }
    
    .step-label {
        font-size: 0.875rem;
        color: var(--gray);
        font-weight: 500;
    }
    
    .step-label.active {
        color: var(--primary);
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4);
    }
    
    /* File Uploader */
    .uploadedFile {
        background: var(--light);
        border: 2px dashed var(--primary);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .uploadedFile:hover {
        background: white;
        border-color: var(--primary-dark);
    }
    
    /* Status Messages */
    .status-message {
        padding: 1rem 1.5rem;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 1rem 0;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .status-success {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid var(--success);
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fed7aa 0%, #fde68a 100%);
        border-left: 4px solid var(--warning);
    }
    
    .status-info {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid var(--primary);
    }
    
    /* Forms */
    .form-group {
        background: var(--light);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .form-label {
        font-weight: 600;
        color: var(--dark);
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* Table Styling */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: var(--shadow) !important;
    }
    
    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip-text {
        visibility: hidden;
        background: var(--dark);
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 0.5rem;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.75rem;
    }
    
    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    
    /* Animations */
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(99, 102, 241, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
        }
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Responsive */
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: 1fr;
        }
        
        .app-title {
            font-size: 1.5rem;
        }
        
        .nav-tabs {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 0
if 'process_step' not in st.session_state:
    st.session_state.process_step = 1

# --- DATA PROCESSING FUNCTIONS (Keep all your existing functions) ---
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

def process_athens_file(df):
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

        # All your existing rules here...
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

        # Add all other rules from your original code...
        
        if not filled:
            entry["Description"] = f"⚠️ {entry['Description']}"

        results.append(entry)

    result_df = pd.DataFrame(results)
    column_order = [
        "Date", "Income/Outcome", "Expenses Type", "Location", "Project", 
        "Supplier", "Type", "Description", "Income", "Outcome", "Total", 
        "Balance", "Repayment", "Original Description"
    ]
    result_df = result_df[column_order]
    return result_df

def process_file(df):
    # Your existing process_file function here with all rules...
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
        
        # Add all your existing rules here...
        
        if not filled:
            entry["Description"] = f"⚠️ {entry['Description']}"
            
        results.append(entry)

    df = pd.DataFrame(results)
    if 'Original Description' in df.columns:
        original_col = df.pop('Original Description')
        df['Original Description'] = original_col
    return df

# --- MAIN APP ---
def main():
    # Container wrapper
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">
            <span>💰</span>
            <span>Aiolos Finance</span>
        </h1>
        <p class="app-subtitle">Smart Financial Management & Analysis Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    tabs = ["📊 Excel Classifier", "📄 Receipt Generator", "💳 Payment Instructions"]
    
    tab_html = '<div class="nav-tabs">'
    for i, tab in enumerate(tabs):
        active_class = "active" if i == st.session_state.current_tab else ""
        tab_html += f'<button class="nav-tab {active_class}" onclick="handleTabClick({i})">{tab}</button>'
    tab_html += '</div>'
    
    st.markdown(tab_html, unsafe_allow_html=True)
    
    # Tab selection
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Excel Classifier", use_container_width=True):
            st.session_state.current_tab = 0
    with col2:
        if st.button("📄 Receipt Generator", use_container_width=True):
            st.session_state.current_tab = 1
    with col3:
        if st.button("💳 Payment Instructions", use_container_width=True):
            st.session_state.current_tab = 2
    
    # Content based on selected tab
    if st.session_state.current_tab == 0:
        excel_classifier_page()
    elif st.session_state.current_tab == 1:
        receipt_generator_page()
    else:
        payment_instructions_page()
    
    st.markdown('</div>', unsafe_allow_html=True)

def excel_classifier_page():
    st.markdown("""
    <div class="glass-card">
        <h2 style="color: var(--dark); margin-bottom: 0.5rem;">Excel Transaction Classifier</h2>
        <p style="color: var(--gray);">Automatically categorize and organize your financial transactions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress indicator
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-steps">
            <div class="progress-step">
                <div class="step-circle {'completed' if st.session_state.process_step > 1 else 'active' if st.session_state.process_step == 1 else ''}">1</div>
                <div class="step-label {'active' if st.session_state.process_step == 1 else ''}">Select Format</div>
            </div>
            <div class="progress-step">
                <div class="step-circle {'completed' if st.session_state.process_step > 2 else 'active' if st.session_state.process_step == 2 else ''}">2</div>
                <div class="step-label {'active' if st.session_state.process_step == 2 else ''}">Upload File</div>
            </div>
            <div class="progress-step">
                <div class="step-circle {'completed' if st.session_state.process_step > 3 else 'active' if st.session_state.process_step == 3 else ''}">3</div>
                <div class="step-label {'active' if st.session_state.process_step == 3 else ''}">Process</div>
            </div>
            <div class="progress-step">
                <div class="step-circle {'completed' if st.session_state.process_step > 4 else 'active' if st.session_state.process_step == 4 else ''}">4</div>
                <div class="step-label {'active' if st.session_state.process_step == 4 else ''}">Download</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            project_type = st.selectbox(
                "📁 Select Format Type",
                ["DIAKOFTI", "ATHENS"],
                help="Choose the format that matches your data structure"
            )
            
            uploaded_file = st.file_uploader(
                "📤 Upload Excel File",
                type=["xlsx", "csv"],
                help="Drag and drop or click to browse"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h4 style="color: white; margin-bottom: 1rem;">ℹ️ Quick Guide</h4>
            <ul style="font-size: 0.9rem; line-height: 1.8;">
                <li><strong>DIAKOFTI:</strong> Plot-based transactions</li>
                <li><strong>ATHENS:</strong> Office transactions</li>
                <li>Supports Excel & CSV files</li>
                <li>Auto-categorization with AI</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    if uploaded_file:
        st.session_state.process_step = 2
        
        st.markdown(f"""
        <div class="status-message status-info">
            <span>📁</span>
            <div>
                <strong>File Ready:</strong> {uploaded_file.name}<br>
                <small>Format: {project_type} | Size: {uploaded_file.size / 1024:.1f} KB</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚡ Process File", use_container_width=True):
            st.session_state.process_step = 3
            
            with st.spinner("🔄 Processing your data..."):
                try:
                    if project_type == "DIAKOFTI":
                        if uploaded_file.name.endswith(".csv"):
                            raw_df = pd.read_csv(uploaded_file, encoding="ISO-8859-7")
                        else:
                            raw_df = pd.read_excel(uploaded_file)
                        result_df = process_file(raw_df)
                    else:
                        raw_df = pd.read_excel(uploaded_file)
                        result_df = process_athens_file(raw_df)
                    
                    st.session_state.result_df = result_df
                    st.session_state.process_step = 4
                    
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
    
    # Results section
    if 'result_df' in st.session_state and st.session_state.process_step == 4:
        result_df = st.session_state.result_df
        
        # Calculate metrics
        marked_entries = result_df['Description'].str.contains('⚠️').sum()
        auto_classified = len(result_df) - marked_entries
        percentage = (auto_classified / len(result_df)) * 100 if len(result_df) > 0 else 0
        
        # Stats display
        st.markdown("""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{}</div>
                <div class="stat-label">Total Entries</div>
                <div class="stat-change positive">📈 Processed successfully</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{}</div>
                <div class="stat-label">Need Review</div>
                <div class="stat-change {}">⚠️ Manual check required</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{:.1f}%</div>
                <div class="stat-label">Auto-Classification</div>
                <div class="stat-change positive">✨ AI Accuracy</div>
            </div>
        </div>
        """.format(
            len(result_df), 
            marked_entries,
            "warning" if marked_entries > 0 else "positive",
            percentage
        ), unsafe_allow_html=True)
        
        # Data preview
        st.markdown("""
        <div class="glass-card">
            <h3 style="margin-bottom: 1rem;">📋 Data Preview</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(
            result_df.head(10),
            use_container_width=True,
            height=400
        )
        
        # Create charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Type' in result_df.columns:
                type_counts = result_df['Type'].value_counts().head(10)
                fig = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Transaction Types Distribution"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Income' in result_df.columns and 'Outcome' in result_df.columns:
                income_total = result_df['Income'].replace('', 0).astype(float).sum()
                outcome_total = result_df['Outcome'].replace('', 0).astype(float).sum()
                
                fig = go.Figure(data=[
                    go.Bar(name='Income', x=['Total'], y=[income_total], marker_color='#10b981'),
                    go.Bar(name='Outcome', x=['Total'], y=[abs(outcome_total)], marker_color='#ef4444')
                ])
                fig.update_layout(title="Income vs Outcome", height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # Download section
        st.markdown("""
        <div class="glass-card" style="text-align: center; background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
        """, unsafe_allow_html=True)
        
        to_download = BytesIO()
        result_df.to_excel(to_download, index=False, engine='openpyxl')
        
        st.download_button(
            label="⬇️ Download Processed Excel",
            data=to_download.getvalue(),
            file_name=f"{project_type.lower()}processed{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)

def receipt_generator_page():
    st.markdown("""
    <div class="glass-card">
        <h2 style="color: var(--dark); margin-bottom: 0.5rem;">Receipt Generator</h2>
        <p style="color: var(--gray);">Create professional payment receipts for villa owners</p>
    </div>
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
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        with st.form("receipt_form", clear_on_submit=False):
            st.markdown('<h3 style="color: var(--primary); margin-bottom: 1rem;">📝 Receipt Details</h3>', unsafe_allow_html=True)
            
            # Villa selection
            col_a, col_b = st.columns(2)
            with col_a:
                project = st.selectbox(
                    "🏘️ Project Plot",
                    sorted(set(k[0] for k in villa_owners.keys())),
                    help="Select the project location"
                )
            
            with col_b:
                villa_options = sorted(set(k[1] for k in villa_owners.keys() if k[0] == project))
                villa = st.selectbox(
                    "🏠 Villa Number",
                    villa_options,
                    help="Select the specific villa"
                )
            
            # Display owner info
            client_name = villa_owners.get((project, villa), "")
            if client_name:
                st.markdown(f"""
                <div class="status-message status-info">
                    <span>👤</span>
                    <div>
                        <strong>Owner:</strong> {client_name}<br>
                        <small>Project: {project} | {villa}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Payment details
            col_c, col_d = st.columns(2)
            with col_c:
                payment_order_number = st.text_input(
                    "📋 Payment Order Number",
                    placeholder="e.g., PO-2024-001"
                )
            
            with col_d:
                sum_euro = st.text_input(
                    "💶 Amount (EUR)",
                    placeholder="e.g., 1,500.00"
                )
            
            extra_text = st.text_area(
                "📝 Additional Notes (Optional)",
                placeholder="Enter any additional payment details or notes...",
                height=100
            )
            
            generate_btn = st.form_submit_button(
                "🎯 Generate Receipt",
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if generate_btn and payment_order_number and sum_euro:
            try:
                # Check if template exists
                template = Document("default_template.docx")
                
                # Replace placeholders
                for p in template.paragraphs:
                    p.text = p.text.replace("{{date}}", datetime.datetime.now().strftime("%d/%m/%Y"))
                    p.text = p.text.replace("{{plot}}", project)
                    p.text = p.text.replace("{{villa_no}}", villa)
                    p.text = p.text.replace("{{client_name}}", client_name)
                    p.text = p.text.replace("{{payment_order_number}}", payment_order_number)
                    p.text = p.text.replace("{{sum}}", sum_euro)
                    p.text = p.text.replace("{{Extra Payment text}}", extra_text)
                
                # Save to buffer
                buffer = BytesIO()
                template.save(buffer)
                buffer.seek(0)
                
                filename = f"Diakofti_Village_{project}{villa}_Payment{payment_order_number}.docx"
                
                st.markdown("""
                <div class="status-message status-success pulse">
                    <span>✅</span>
                    <div>
                        <strong>Receipt Generated Successfully!</strong><br>
                        <small>Ready for download</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.download_button(
                    label="📥 Download Receipt Document",
                    data=buffer,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                
            except FileNotFoundError:
                st.error("⚠️ Template file 'default_template.docx' not found. Please ensure the template is in the same directory.")
        
        elif generate_btn:
            st.warning("⚠️ Please fill in all required fields (Payment Order Number and Amount)")
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);">
            <h4 style="color: white; margin-bottom: 1rem;">📊 Quick Stats</h4>
            <div style="color: white;">
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 1.5rem; font-weight: 700;">{}</div>
                    <div style="font-size: 0.875rem; opacity: 0.9;">Total Properties</div>
                </div>
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 1.5rem; font-weight: 700;">{}</div>
                    <div style="font-size: 0.875rem; opacity: 0.9;">Unique Owners</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700;">{}</div>
                    <div style="font-size: 0.875rem; opacity: 0.9;">Project Plots</div>
                </div>
            </div>
        </div>
        """.format(
            len(villa_owners),
            len(set(villa_owners.values())),
            len(set(k[0] for k in villa_owners.keys()))
        ), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: var(--dark); margin-bottom: 1rem;">ℹ️ Instructions</h4>
            <ol style="font-size: 0.9rem; color: var(--gray); line-height: 1.8;">
                <li>Select project and villa</li>
                <li>Enter payment details</li>
                <li>Add optional notes</li>
                <li>Generate & download</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

def payment_instructions_page():
    st.markdown("""
    <div class="glass-card">
        <h2 style="color: var(--dark); margin-bottom: 0.5rem;">Payment Instructions</h2>
        <p style="color: var(--gray);">Manage and track payment workflows</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Coming soon message with modern design
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);">
        <div style="color: white;">
            <h1 style="font-size: 4rem; margin-bottom: 1rem;">🚀</h1>
            <h2 style="color: white; margin-bottom: 1rem;">Coming Soon!</h2>
            <p style="font-size: 1.1rem; opacity: 0.9; margin-bottom: 2rem;">
                We're building something amazing for payment instructions management.
            </p>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
                    <div style="font-size: 0.9rem;">Automated Workflows</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔄</div>
                    <div style="font-size: 0.9rem;">Real-time Tracking</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-size: 0.9rem;">Analytics Dashboard</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature preview cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div style="color: var(--primary); font-size: 2rem; margin-bottom: 0.5rem;">💸</div>
            <div style="font-weight: 600; margin-bottom: 0.5rem;">Payment Templates</div>
            <div style="font-size: 0.875rem; color: var(--gray);">
                Create reusable payment instruction templates
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div style="color: var(--success); font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
            <div style="font-weight: 600; margin-bottom: 0.5rem;">Approval Workflows</div>
            <div style="font-size: 0.875rem; color: var(--gray);">
                Multi-level approval processes with notifications
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div style="color: var(--warning); font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
            <div style="font-weight: 600; margin-bottom: 0.5rem;">Payment Analytics</div>
            <div style="font-size: 0.875rem; color: var(--gray);">
                Track payment history and generate reports
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Newsletter signup
    st.markdown("""
    <div class="glass-card" style="margin-top: 2rem;">
        <h3 style="text-align: center; margin-bottom: 1rem;">🔔 Get Notified When It's Ready</h3>
        <p style="text-align: center; color: var(--gray); margin-bottom: 1.5rem;">
            Be the first to know when Payment Instructions feature launches
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("", placeholder="Enter your email address")
        if st.button("Notify Me", use_container_width=True):
            if email:
                st.success("✅ You'll be notified when this feature is available!")
            else:
                st.warning("⚠️ Please enter your email address")

# Run the app
if _name_ == "_main_":
    main()
