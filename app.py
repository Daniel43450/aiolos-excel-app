import streamlit as st
import pandas as pd
import re
import datetime
from io import BytesIO
from docx import Document

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
    
    /* Custom header */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
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
        gap: 2rem;
        background: white;
        padding: 0.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 2rem;
        background: transparent;
        border-radius: 8px;
        font-weight: 500;
        color: #666;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f8f9fa;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
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
        border-color: #667eea;
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
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    /* Progress indicator */
    .progress-bar {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
        position: relative;
    }
    
    .progress-step {
        flex: 1;
        text-align: center;
        position: relative;
        z-index: 1;
    }
    
    .progress-step::before {
        content: '';
        position: absolute;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #e0e0e0;
        z-index: -1;
    }
    
    .progress-step.active::before {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .progress-step.completed::before {
        background: #4caf50;
    }
    
    .progress-label {
        margin-top: 55px;
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Data preview */
    .dataframe {
        border: none !important;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .dataframe tbody tr:hover {
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("""
<div class="app-header">
    <h1 class="app-title">💼 Aiolos Financial Tools</h1>
    <p class="app-subtitle">Smart financial management made simple</p>
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
        # ============================================
        # Example rules (add your actual rules below):
        
        # Rule 1: Bank fees
        if "COM POI" in desc or "COM POO" in desc:
            entry["Type"] = "Bank"
            entry["Supplier"] = "Bank"
            entry["Description"] = "Bank fees"
            filled = True
        
        # Rule 2: Marketing
        if "FACEBOOK" in desc or "GOOGLE" in desc:
            entry["Type"] = "Marketing"
            entry["Supplier"] = "Marketing"
            entry["Description"] = "Marketing Services fee"
            filled = True
        
        # 🔴 ADD MORE DIAKOFTI RULES HERE
        # if "KEYWORD" in desc:
        #     entry["Type"] = "Your Type"
        #     entry["Supplier"] = "Your Supplier"
        #     entry["Description"] = "Your Description"
        #     filled = True
        
        # ============================================
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
tab1, tab2, tab3 = st.tabs(["📊 Excel Classifier", "📄 Receipt Generator", "ℹ️ Help"])

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
        if st.button("🚀 Process File", use_container_width=True):
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
# TAB 2: RECEIPT GENERATOR
# ============================================
with tab2:
    # Villa owners database
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
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📄 Generate Payment Receipt")
        
        # Project selection
        project = st.selectbox(
            "Select Project",
            sorted(set(k[0] for k in villa_owners)),
            help="Choose the project plot"
        )
        
        # Villa selection
        villa_options = sorted(set(k[1] for k in villa_owners if k[0] == project))
        villa = st.selectbox(
            "Select Villa",
            villa_options,
            help="Select the villa number"
        )
        
        # Display owner name
        client_name = villa_owners.get((project, villa), "")
        if client_name:
            st.info(f"**Owner:** {client_name}")
        
        # Payment details
        st.markdown("### 💳 Payment Details")
        payment_order = st.text_input("Payment Order Number", placeholder="e.g., 12345")
        amount = st.text_input("Amount in Euro (€)", placeholder="e.g., 5000")
        extra_text = st.text_area("Additional Notes (Optional)", placeholder="Any additional payment information...")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📌 Receipt Info")
        st.markdown("""
        **What you'll get:**
        - Professional Word document
        - Auto-filled owner details
        - Ready to send format
        
        **Required:**
        - Payment order number
        - Amount in Euro
        
        **Optional:**
        - Additional notes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate receipt
    if st.button("📄 Generate Receipt", use_container_width=True):
        if payment_order and amount:
            try:
                # Note: You'll need to have the template file
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
                
                filename = f"Receipt_{project}_{villa}_Order_{payment_order}.docx"
                
                st.markdown('<div class="success-msg">✅ Receipt generated successfully!</div>', unsafe_allow_html=True)
                
                st.download_button(
                    label="📥 Download Receipt",
                    data=buffer,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except FileNotFoundError:
                st.error("❌ Template file 'default_template.docx' not found. Please add it to the app directory.")
            except Exception as e:
                st.error(f"❌ Error generating receipt: {str(e)}")
        else:
            st.warning("⚠️ Please fill in Payment Order Number and Amount")

# ============================================
# TAB 3: HELP
# ============================================
with tab3:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### 🔧 How to Use This App")
    
    st.markdown("""
    #### Excel Classifier
    1. **Select Format**: Choose between DIAKOFTI (plot-based) or ATHENS (office) format
    2. **Upload File**: Upload your Excel or CSV file
    3. **Process**: Click the Process button to categorize transactions
    4. **Review**: Check entries marked with 🟨 - these need manual review
    5. **Download**: Download the processed file with all categorizations
    
    #### Receipt Generator
    1. **Select Villa**: Choose project and villa number
    2. **Enter Details**: Add payment order number and amount
    3. **Generate**: Click to create a Word document receipt
    4. **Download**: Save the receipt for your records
    
    #### Adding Rules
    To add classification rules, edit the code in the processing functions:
    - **DIAKOFTI Rules**: Look for the section marked "🔴 DIAKOFTI RULES"
    - **ATHENS Rules**: Look for the section marked "🔵 ATHENS RULES"
    
    #### Support
    For issues or questions, please contact the development team.
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Version info
    st.markdown("---")
    st.markdown("**Version:** 2.0.0 | **Last Updated:** " + datetime.datetime.now().strftime("%Y-%m-%d"))
