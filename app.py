import streamlit as st
import pandas as pd
import re
import datetime
import os
from io import BytesIO
import docx
import tempfile
from PIL import Image
import base64
import locale
import shutil
import glob

# Set locale for number formatting
locale.setlocale(locale.LC_ALL, '') 

# --- APPLICATION SETUP ---
st.set_page_config(page_title="Aiolos Management System", layout="wide", initial_sidebar_state="expanded")
st.sidebar.title("Navigation")
st.sidebar.info("Select a section to continue")

# --- COMMON STYLES ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
        
        body {
            font-family: 'Montserrat', sans-serif;
        }
        .stApp {
            background-color: #f8f9fa;
        }
        .decor-box {
            background-color: #eef5ff;
            border-left: 6px solid #003366;
            padding: 1.2em;
            margin: 2em auto;
            width: 96%;
            border-radius: 8px;
            font-size: 1em;
            color: #003366;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .stButton>button {
            background-color: #003366;
            color: white;
            font-weight: 600;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            border: none;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #004080;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .logo-container {
            display: flex;
            justify-content: center;
            margin: 20px auto;
        }
        .logo {
            width: 150px;
            border-radius: 75px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }
        .logo:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 15px rgba(0,0,0,0.15);
        }
        .sidebar .sidebar-content {
            background-color: #002142;
            color: white;
        }
        h1, h2, h3 {
            color: #002142;
            font-weight: 600;
        }
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input {
            border-radius: 5px;
            border: 1px solid #cfd8dc;
            padding: 0.5rem;
        }
        .stTextArea>div>div>textarea {
            border-radius: 5px;
            border: 1px solid #cfd8dc;
            padding: 0.5rem;
        }
        .info-card {
            background-color: #f1f8ff;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            border: 1px solid #cfd8dc;
        }
        .success-message {
            background-color: #e6f4ea;
            color: #137333;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid #137333;
        }
        .stSelectbox>div>div {
            border-radius: 5px;
            border: 1px solid #cfd8dc;
        }
        .stFileUploader>div>button {
            background-color: #f8f9fa;
            border: 1px dashed #cfd8dc;
        }
        footer {
            visibility: hidden;
        }
        .section-title {
            border-bottom: 2px solid #eef2f5;
            padding-bottom: 8px;
            margin-bottom: 16px;
            color: #002142;
        }
        /* Add a custom footer */
        .footer-custom {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f8f9fa;
            text-align: center;
            padding: 10px;
            font-size: 12px;
            border-top: 1px solid #eef2f5;
            color: #64748b;
        }
        /* PDF Preview styling */
        .pdf-preview {
            width: 100%;
            height: 500px;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }
        /* Receipt batch processing styles */
        .batch-form {
            background-color: #f1f8ff;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            border: 1px solid #cfd8dc;
        }
        /* Receipt history section */
        .receipt-history {
            margin-top: 30px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #eef2f5;
        }
        .receipt-card {
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .receipt-info {
            flex-grow: 1;
        }
        .receipt-actions {
            display: flex;
            gap: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGO ---
st.markdown("""
    <div class="logo-container">
        <img class="logo" src='https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG' alt='Aiolos Logo'>
    </div>
""", unsafe_allow_html=True)

# --- CREATE OUTPUT DIRECTORIES ---
def ensure_directories():
    # Create directories if they don't exist
    os.makedirs("receipts_output/docx", exist_ok=True)
    os.makedirs("receipts_output/pdf", exist_ok=True)
    return "receipts_output"

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Excel Processor", "Receipt Generator", "Receipt History"])

# --- EXCEL PROCESSOR PAGE ---
if page == "Excel Processor":
    # --- Decorative Section ---
    st.title("Excel Processor")
    st.markdown("""
        <div class='decor-box'>
            Upload your financial Excel statement and get an automatically categorized version ready for download — powered by Aiolos.
        </div>
    """, unsafe_allow_html=True)

    # --- PROJECT SELECTION ---
    project_type = st.selectbox("Choose Excel Format:", ["DIAKOFTI"], index=0)

    # --- FILE UPLOAD ---
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "csv"], key="excel_uploader")

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

    # --- MAIN PROCESSING FUNCTION ---
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

            # Highlight in yellow if not matched to a rule
            if not filled:
                entry["Description"] = f"🟨 {entry['Description']}"

            results.append(entry)

        df = pd.DataFrame(results)
        if 'Original Description' in df.columns:
            original_col = df.pop('Original Description')
            df['Original Description'] = original_col
        return df

    # --- RUN ---
    if uploaded_file:
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
            file_name=f"aiolos_processed_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# --- RECEIPT GENERATOR PAGE ---
# --- RECEIPT GENERATOR PAGE ---
page = st.radio("Select Page", ["Receipt Generator", "Buyer Directory"])

if page == "Receipt Generator":
    st.title("Receipt Generator")
    st.markdown("""
        <div class='decor-box'>
            Create professional receipts by uploading a template and filling in details — powered by Aiolos.
        </div>
    """, unsafe_allow_html=True)

    # Make sure directories exist
    output_dir = ensure_directories()

    buyers_data = [
        {"plot": "Y3", "villa": "Villa 2", "name": "Eli Malka"},
        {"plot": "Y3", "villa": "Villa 3", "name": "Ran Hai"},
        {"plot": "Y3", "villa": "Villa 5", "name": "Eliyahu Ovadia"},
        {"plot": "Y4-7", "villa": "Villa 9", "name": "Elad Shimon Nissenholtz"},
        {"plot": "Y4-7", "villa": "Villa 10", "name": "Dan Dikanoff"},
        {"plot": "G2", "villa": "Villa 1", "name": "Ester Danziger"},
        {"plot": "G2", "villa": "Villa 2", "name": "Gil Bar el"},
        {"plot": "G2", "villa": "Villa 4", "name": "Michael Gurevich"},
        {"plot": "G2", "villa": "Villa 5", "name": "Alexander Gurevich"},
        {"plot": "G2", "villa": "Villa 6", "name": "Linkova Oksana M"},
        {"plot": "G2", "villa": "Villa 7", "name": "Ofir Laor"},
        {"plot": "G2", "villa": "Villa 8", "name": "Patrice Daniel Giami"},
        {"plot": "G13", "villa": "Villa 2", "name": "Nir Goldberg"},
        {"plot": "G13", "villa": "Villa 3", "name": "Nir Goldberg"},
        {"plot": "G13", "villa": "Villa 4", "name": "Keren Goldberg"},
        {"plot": "G13", "villa": "Villa 5", "name": "Rachel Goldberg Keidar"},
        {"plot": "B5", "villa": "Villa 1", "name": "Keren Goldberg"},
        {"plot": "R4", "villa": "Villa 1", "name": "Nirit Mizrahi"},
        {"plot": "R4", "villa": "Villa 1", "name": "Itah Ella"}
    ]

    with st.form("receipt_form"):
        col1, col2 = st.columns(2)
        with col1:
            plot_input = st.selectbox("Plot", sorted(set(b["plot"] for b in buyers_data)))
            villa_input = st.text_input("Villa (e.g., Villa 2)")
            payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Credit Card", "Cash", "Check"])
            amount = st.number_input("Amount (€)", min_value=0.0, step=10.0)
        with col2:
            description = st.text_area("Description of Services")
            tax_rate = st.slider("Tax Rate (%)", 0, 24, 24)
            receipt_date = st.date_input("Receipt Date", datetime.datetime.now())

        submitted = st.form_submit_button("Generate Receipt")

    if submitted:
        customer_name = next((b['name'] for b in buyers_data if b['plot'] == plot_input and b['villa'].lower() == villa_input.lower()), None)

        if not customer_name:
            st.error("No buyer found for the provided plot and villa.")
        elif not description or amount <= 0:
            st.error("Please fill in all required fields.")
        else:
            tax_amount = amount * (tax_rate / 100)
            total_amount = amount + tax_amount

            receipt_number = f"AIOLOS-{datetime.datetime.now().strftime('%Y%m')}-{plot_input}-{villa_input.replace(' ', '')}"

            doc = docx.Document()
            doc.add_heading("Receipt", level=1)
            doc.add_paragraph(f"Receipt Number: {receipt_number}")
            doc.add_paragraph(f"Date: {receipt_date.strftime('%d/%m/%Y')}")
            doc.add_paragraph(f"Customer: {customer_name}")
            doc.add_paragraph(f"Plot: {plot_input}, Villa: {villa_input}")
            doc.add_paragraph(f"Description: {description}")
            doc.add_paragraph(f"Amount: €{amount:.2f}")
            doc.add_paragraph(f"Tax Rate: {tax_rate}%")
            doc.add_paragraph(f"Tax Amount: €{tax_amount:.2f}")
            doc.add_paragraph(f"Total Amount: €{total_amount:.2f}")
            doc.add_paragraph(f"Payment Method: {payment_method}")

            safe_name = re.sub(r'[^\w\s-]', '', customer_name).strip().replace(' ', '_')
            filename = f"{receipt_number}_{safe_name}.docx"
            filepath = os.path.join(output_dir, filename)
            doc.save(filepath)

            with open(filepath, "rb") as f:
                st.download_button(
                    label="Download Receipt (DOCX)",
                    data=f.read(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

elif page == "Buyer Directory":
    st.title("Buyer Directory")
    st.markdown("Below is the list of all current buyers by plot and villa.")

    df = pd.DataFrame(buyers_data)
    df = df.sort_values(by=["plot", "villa"])
    st.dataframe(df)
# --- RECEIPT HISTORY PAGE ---
elif page == "Receipt History":
    st.title("Receipt History")
    st.markdown("""
        <div class='decor-box'>
            View and manage your previously generated receipts — powered by Aiolos.
        </div>
    """, unsafe_allow_html=True)
    
    # Make sure directories exist
    output_dir = ensure_directories()
    
    # --- DETECT EXISTING RECEIPTS ---
    # Function to scan directories and find receipts
    def scan_for_receipts():
        receipts = []
        if not os.path.exists(os.path.join(output_dir, "pdf")):
            return receipts
            
        pdf_files = glob.glob(os.path.join(output_dir, "pdf", "*.pdf"))
        
        for pdf_file in pdf_files:
            filename = os.path.basename(pdf_file)
            # Try to extract receipt number and customer from filename
            match = re.match(r"([^_]+)_(.+)\.pdf", filename)
            
            if match:
                receipt_number = match.group(1)
                customer_name = match.group(2).replace("_", " ")
                
                # Check if corresponding DOCX exists
                docx_path = os.path.join(output_dir, "docx", filename.replace(".pdf", ".docx"))
                docx_exists = os.path.exists(docx_path)
                
                file_stats = os.stat(pdf_file)
                created_time = datetime.datetime.fromtimestamp(file_stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                
                receipts.append({
                    "number": receipt_number,
                    "customer": customer_name,
                    "pdf_path": pdf_file,
                    "docx_path": docx_path if docx_exists else None,
                    "created_at": created_time
                })
        
        return sorted(receipts, key=lambda x: x["created_at"], reverse=True)
    
    # Merge session history with disk scan
    all_receipts = []
    
    # Get session history
    if 'receipt_history' in st.session_state:
        all_receipts.extend(st.session_state.receipt_history)
    
    # Add receipts found on disk that aren't in session history
    disk_receipts = scan_for_receipts()
    session_receipt_paths = [r.get("pdf_path", "") for r in all_receipts]
    
    for disk_receipt in disk_receipts:
        if disk_receipt["pdf_path"] not in session_receipt_paths:
            all_receipts.append(disk_receipt)
    
    # Remove duplicates and sort by date
    unique_receipts = {}
    for receipt in all_receipts:
        if "pdf_path" in receipt and receipt["pdf_path"]:
            unique_receipts[receipt["pdf_path"]] = receipt
    
    receipt_list = list(unique_receipts.values())
    receipt_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Display receipts
    if receipt_list:
        # Search functionality
        search_query = st.text_input("Search receipts by number or customer name:", "")
        
        filtered_receipts = receipt_list
        if search_query:
            filtered_receipts = [r for r in receipt_list if 
                                 search_query.lower() in r.get("number", "").lower() or 
                                 search_query.lower() in r.get("customer", "").lower()]
        
        st.subheader(f"Found {len(filtered_receipts)} Receipts")
        
        # Display receipts in a nice format
        for receipt in filtered_receipts:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.markdown(f"**Receipt:** {receipt.get('number', 'Unknown')}")
                    st.markdown(f"Customer: {receipt.get('customer', 'Unknown')}")
                    
                with col2:
                    st.markdown(f"Date: {receipt.get('date', 'Unknown')}" if "date" in receipt else f"Created: {receipt.get('created_at', 'Unknown')}")
                    if "amount" in receipt:
                        st.markdown(f"Amount: €{receipt.get('amount', 0):.2f}")
                
                with col3:
                    # Download buttons
                    if "pdf_path" in receipt and receipt["pdf_path"] and os.path.exists(receipt["pdf_path"]):
                        with open(receipt["pdf_path"], "rb") as f:
                            pdf_bytes = f.read()
                            st.download_button(
                                label="PDF",
                                data=pdf_bytes,
                                file_name=os.path.basename(receipt["pdf_path"]),
                                mime="application/pdf",
                                key=f"pdf_{receipt.get('number', '')}_{receipt.get('customer', '')}"
                            )
                    
                    if "docx_path" in receipt and receipt["docx_path"] and os.path.exists(receipt["docx_path"]):
                        with open(receipt["docx_path"], "rb") as f:
                            docx_bytes = f.read()
                            st.download_button(
                                label="DOCX",
                                data=docx_bytes,
                                file_name=os.path.basename(receipt["docx_path"]),
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"docx_{receipt.get('number', '')}_{receipt.get('customer', '')}"
                            )
                
                # Preview button
                if st.button("Preview", key=f"preview_{receipt.get('number', '')}_{receipt.get('customer', '')}"):
                    if "pdf_path" in receipt and receipt["pdf_path"] and os.path.exists(receipt["pdf_path"]):
                        with open(receipt["pdf_path"], "rb") as f:
                            pdf_bytes = f.read()
                            st.markdown(f"""
                                <iframe src="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode('utf-8')}" 
                                        width="100%" height="500" type="application/pdf" class="pdf-preview"></iframe>
                            """, unsafe_allow_html=True)
                
                st.markdown("---")
    else:
        st.markdown("No receipts found. Go to the Receipt Generator page to create some!")
    
    # Export all receipts
    if receipt_list:
        if st.button("Export All Receipts as ZIP"):
            # Create a zip file of all PDFs
            zip_path = os.path.join(output_dir, f"all_receipts_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
            
            import zipfile
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for receipt in receipt_list:
                    if "pdf_path" in receipt and receipt["pdf_path"] and os.path.exists(receipt["pdf_path"]):
                        zipf.write(receipt["pdf_path"], os.path.basename(receipt["pdf_path"]))
            
            # Offer zip download
            with open(zip_path, "rb") as f:
                zip_bytes = f.read()
                
            st.download_button(
                label="Download All PDFs as ZIP",
                data=zip_bytes,
                file_name=os.path.basename(zip_path),
                mime="application/zip",
            )

# --- CUSTOM FOOTER ---
st.markdown("""
    <div class="footer-custom">
        © 2025 Aiolos Management System | Version 1.2.0
    </div>
""", unsafe_allow_html=True)
