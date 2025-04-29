import streamlit as st
import pandas as pd
import re
import datetime
import os
from io import BytesIO
import docx
from docx2pdf import convert
import tempfile
from PIL import Image
import base64
import locale
import shutil
import glob

# Set locale for number formatting
locale.setlocale(locale.LC_ALL, '') GD

# --- APPLICATION SETUP ---
st.set_page_config(page_title="Aiolos Management System", layout="wide", initial_sidebar_state="expanded")

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
elif page == "Receipt Generator":
    st.title("Receipt Generator")
    st.markdown("""
        <div class='decor-box'>
            Create professional receipts by uploading a template and filling in details — powered by Aiolos.
        </div>
    """, unsafe_allow_html=True)
    
    # Make sure directories exist
    output_dir = ensure_directories()
    
    # --- SESSION STATE SETUP ---
    if 'template_path' not in st.session_state:
        st.session_state.template_path = None
    if 'last_generated_receipt' not in st.session_state:
        st.session_state.last_generated_receipt = None
    if 'receipt_history' not in st.session_state:
        st.session_state.receipt_history = []
    
    # --- TEMPLATE UPLOAD ---
    template_col1, template_col2 = st.columns([2, 1])
    
    with template_col1:
        template_file = st.file_uploader("Upload Receipt Template (DOCX)", type=["docx"], key="template_uploader")
    
    with template_col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        if st.button("Use Default Template"):
            # Reference to a default template if available
            if os.path.exists("default_template.docx"):
                st.session_state.template_path = "default_template.docx"
                st.success("Default template loaded!")
            else:
                st.error("Default template not found. Please upload a template.")
    
    if template_file:
        # Save the template temporarily
        temp_dir = tempfile.mkdtemp()
        template_path = os.path.join(temp_dir, "template.docx")
        
        with open(template_path, "wb") as f:
            f.write(template_file.getvalue())
        
        st.session_state.template_path = template_path
        st.success("Template uploaded successfully!")
    
    # --- RECEIPT FORM ---
    if st.session_state.template_path:
        st.subheader("Receipt Details")
        
        # Save form data to session state when filled
        if 'form_filled' not in st.session_state:
            st.session_state.form_filled = False
        
        # Auto-generate receipt number based on date and counter
        if 'receipt_counter' not in st.session_state:
            st.session_state.receipt_counter = len(st.session_state.receipt_history) + 1
        
        today = datetime.datetime.now()
        default_receipt_number = f"AIOLOS-{today.strftime('%Y%m')}-{st.session_state.receipt_counter:03d}"
        
        # Form layout with columns
        col1, col2 = st.columns(2)
        
        with col1:
            receipt_number = st.text_input("Receipt Number", default_receipt_number)
            receipt_date = st.date_input("Receipt Date", today)
            customer_name = st.text_input("Customer Name", "")
            customer_address = st.text_area("Customer Address", "", height=100)
            payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Credit Card", "Cash", "Check"])
        
        with col2:
            description = st.text_area("Description of Services", "", height=100)
            amount = st.number_input("Amount (€)", min_value=0.0, step=10.0)
            tax_rate = st.slider("Tax Rate (%)", 0, 24, 24)
            tax_amount = amount * (tax_rate / 100)
            total_amount = amount + tax_amount
            
            st.info(f"Base Amount: €{amount:.2f}")
            st.info(f"Tax Amount: €{tax_amount:.2f}")
            st.info(f"Total Amount: €{total_amount:.2f}")
            
            # Number to words conversion (optional)
            def number_to_words(num):
                # Simple implementation - could be expanded
                units = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
                teens = ["", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
                tens = ["", "ten", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
                
                if num < 10:
                    return units[num]
                elif 11 <= num < 20:
                    return teens[num - 10]
                elif num < 100:
                    return tens[num // 10] + ("-" + units[num % 10] if num % 10 != 0 else "")
                else:
                    return "amount too large"  # Simplified
            
            # Get integer and decimal parts
            int_part = int(total_amount)
            decimal_part = int((total_amount - int_part) * 100)
            
            amount_in_words = f"{number_to_words(int_part).capitalize()} euros and {number_to_words(decimal_part)} cents"
            
        # --- GENERATE RECEIPT ---
        if st.button("Generate Receipt"):
            if not customer_name or not description or amount <= 0:
                st.error("Please fill in all required fields (Customer Name, Description, and Amount)")
            else:
                # Load the document
                doc = docx.Document(st.session_state.template_path)
                
                # Define replacement dictionary for all placeholders
                replacements = {
                    "[RECEIPT_NUMBER]": receipt_number,
                    "[RECEIPT_DATE]": receipt_date.strftime("%d/%m/%Y"),
                    "[CUSTOMER_NAME]": customer_name,
                    "[CUSTOMER_ADDRESS]": customer_address,
                    "[DESCRIPTION]": description,
                    "[AMOUNT]": f"€{amount:.2f}",
                    "[TAX_RATE]": f"{tax_rate}%",
                    "[TAX_AMOUNT]": f"€{tax_amount:.2f}",
                    "[TOTAL_AMOUNT]": f"€{total_amount:.2f}",
                    "[PAYMENT_METHOD]": payment_method,
                    "[AMOUNT_IN_WORDS]": amount_in_words
                }
                
                # Replace placeholders in all paragraphs
                for paragraph in doc.paragraphs:
                    for key, value in replacements.items():
                        if key in paragraph.text:
                            paragraph.text = paragraph.text.replace(key, value)
                
                # Also replace in tables if they exist
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                for key, value in replacements.items():
                                    if key in paragraph.text:
                                        paragraph.text = paragraph.text.replace(key, value)
                
                # Create sanitized filename (remove special characters)
                safe_customer_name = re.sub(r'[^\w\s-]', '', customer_name).strip().replace(' ', '_')
                safe_receipt_number = re.sub(r'[^\w\s-]', '', receipt_number).strip().replace(' ', '_')
                receipt_filename = f"{safe_receipt_number}_{safe_customer_name}"
                
                # Save paths
                output_docx_path = os.path.join(output_dir, "docx", f"{receipt_filename}.docx")
                output_pdf_path = os.path.join(output_dir, "pdf", f"{receipt_filename}.pdf")
                
                # Save the modified document
                doc.save(output_docx_path)
                
                # Convert to PDF
                try:
                    convert(output_docx_path, output_pdf_path)
                    
                    # Success message with file paths
                    st.success(f"Receipt generated successfully! Files saved to:\n- DOCX: {output_docx_path}\n- PDF: {output_pdf_path}")
                    
                    # Store receipt info in history
                    receipt_info = {
                        "number": receipt_number,
                        "date": receipt_date.strftime("%d/%m/%Y"),
                        "customer": customer_name,
                        "amount": total_amount,
                        "docx_path": output_docx_path,
                        "pdf_path": output_pdf_path,
                        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.receipt_history.append(receipt_info)
                    st.session_state.last_generated_receipt = receipt_info
                    st.session_state.receipt_counter += 1
                    
                    # Create download buttons
                    col1, col2 = st.columns(2)
                    
                    with open(output_pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                        
                    with open(output_docx_path, "rb") as f:
                        docx_bytes = f.read()
                    
                    with col1:
                        st.download_button(
                            label="Download Receipt PDF",
                            data=pdf_bytes,
                            file_name=f"{receipt_filename}.pdf",
                            mime="application/pdf",
                        )
                    
                    with col2:
                        st.download_button(
                            label="Download Receipt DOCX",
                            data=docx_bytes,
                            file_name=f"{receipt_filename}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        )
                    
                    # Display PDF preview
                    st.subheader("Receipt Preview")
                    st.markdown(f"""
                        <iframe src="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode('utf-8')}" 
                                width="100%" height="500" type="application/pdf" class="pdf-preview"></iframe>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error converting to PDF: {e}")
                    
                    # Still offer the DOCX version
                    with open(output_docx_path, "rb") as f:
                        docx_bytes = f.read()
                        
                    st.download_button(
                        label="Download Receipt DOCX",
                        data=docx_bytes,
                        file_name=f"{receipt_filename}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
    else:
        st.info("Please upload a DOCX template with placeholders like [RECEIPT_NUMBER], [RECEIPT_DATE], [CUSTOMER_NAME], etc.")
        
        # Display example placeholders
        st.subheader("Recommended Placeholders")
        placeholders = """
        - [RECEIPT_NUMBER] - The receipt's identifier
        - [RECEIPT_DATE] - The date of the receipt
        - [CUSTOMER_NAME] - Name of the customer
        - [CUSTOMER_ADDRESS] - Full address of the customer
        - [DESCRIPTION] - Description of services provided
        - [AMOUNT] - Base amount before tax
        - [TAX_RATE] - Tax percentage
        - [TAX_AMOUNT] - Calculated tax amount
        - [TOTAL_AMOUNT] - Total amount including tax
        - [PAYMENT_METHOD] - Method of payment
        - [AMOUNT_IN_WORDS] - Total amount expressed in words
        """
        st.code(placeholders, language="markdown")
        
    # --- BATCH RECEIPT GENERATION ---
    st.markdown("---")
    with st.expander("Batch Receipt Generation"):
        st.markdown("""
            <div class="batch-form">
                <h3>Generate Multiple Receipts from CSV</h3>
                <p>Upload a CSV file with receipt details to generate multiple receipts at once.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # CSV upload
        batch_file = st.file_uploader("Upload CSV with Receipt Data", type=["csv"], key="batch_uploader")
        
        if batch_file and st.session_state.template_path:
            try:
                # Load CSV data
                batch_df = pd.read_csv(batch_file)
                
                # Display preview
                st.subheader("CSV Preview")
                st.dataframe(batch_df)
                
                # Check required columns
                required_columns = ["receipt_number", "customer_name", "description", "amount", "tax_rate"]
                missing_columns = [col for col in required_columns if col not in batch_df.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                    st.info("Your CSV must include: receipt_number, customer_name, description, amount, tax_rate")
                else:
                    if st.button("Generate Batch Receipts"):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Process each row
                        successful_receipts = []
                        failed_receipts = []
                        
                        for i, row in batch_df.iterrows():
                            progress = (i + 1) / len(batch_df)
                            progress_bar.progress(progress)
                            status_text.text(f"Processing receipt {i+1} of {len(batch_df)}: {row['receipt_number']}")
                            
                            try:
                                # Get row data with defaults
                                receipt_number = str(row["receipt_number"])
                                receipt_date = datetime.datetime.strptime(str(row.get("receipt_date", datetime.datetime.now().strftime("%Y-%m-%d"))), "%Y-%m-%d").date()
                                customer_name = str(row["customer_name"])
                                customer_address = str(row.get("customer_address", ""))
                                description = str(row["description"])
                                amount = float(row["amount"])
                                tax_rate = float(row["tax_rate"])
                                payment_method = str(row.get("payment_method", "Bank Transfer"))
                                
                                # Calculate amounts
                                tax_amount = amount * (tax_rate / 100)
                                total_amount = amount + tax_amount
                                
                                # Load document
                                doc = docx.Document(st.session_state.template_path)
                                
                                # Create replacements dictionary
                                replacements = {
                                    "[RECEIPT_NUMBER]": receipt_number,
                                    "[RECEIPT_DATE]": receipt_date.strftime("%d/%m/%Y"),
                                    "[CUSTOMER_NAME]": customer_name,
                                    "[CUSTOMER_ADDRESS]": customer_address,
                                    "[DESCRIPTION]": description,
                                    "[AMOUNT]": f"€{amount:.2f}",
                                    "[TAX_RATE]": f"{tax_rate}%",
                                    "[TAX_AMOUNT]": f"€{tax_amount:.2f}",
                                    "[TOTAL_AMOUNT]": f"€{total_amount:.2f}",
                                    "[PAYMENT_METHOD]": payment_method
                                }
                                
                                # Apply replacements
                                for paragraph in doc.paragraphs:
                                    for key, value in replacements.items():
                                        if key in paragraph.text:
                                            paragraph.text = paragraph.text.replace(key, value)
                                
                                # Also in tables
                                for table in doc.tables:
                                    for row in table.rows:
                                        for cell in row.cells:
                                            for paragraph in cell.paragraphs:
                                                for key, value in replacements.items():
                                                    if key in paragraph.text:
                                                        paragraph.text = paragraph.text.replace(key, value)
                                
                                # Create filenames
                                safe_customer_name = re.sub(r'[^\w\s-]', '', customer_name).strip().replace(' ', '_')
                                safe_receipt_number = re.sub(r'[^\w\s-]', '', receipt_number).strip().replace(' ', '_')
                                receipt_filename = f"{safe_receipt_number}_{safe_customer_name}"
                                
                                # Save paths
                                output_docx_path = os.path.join(output_dir, "docx", f"{receipt_filename}.docx")
                                output_pdf_path = os.path.join(output_dir, "pdf", f"{receipt_filename}.pdf")
                                
                                # Save the document
                                doc.save(output_docx_path)
                                
                                # Convert to PDF
                                convert(output_docx_path, output_pdf_path)
                                
                                # Add to successful list
                                receipt_info = {
                                    "number": receipt_number,
                                    "date": receipt_date.strftime("%d/%m/%Y"),
                                    "customer": customer_name,
                                    "amount": total_amount,
                                    "docx_path": output_docx_path,
                                    "pdf_path": output_pdf_path,
                                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                
                                successful_receipts.append(receipt_info)
                                st.session_state.receipt_history.append(receipt_info)
                            
                            except Exception as e:
                                failed_receipts.append({
                                    "receipt_number": receipt_number,
                                    "customer_name": customer_name,
                                    "error": str(e)
                                })
                        
                        # Show results
                        progress_bar.progress(1.0)
                        status_text.text("Batch processing complete!")
                        
                        if successful_receipts:
                            st.success(f"Successfully generated {len(successful_receipts)} receipts!")
                            
                            # Create a zip file of all PDFs
                            zip_path = os.path.join(output_dir, f"batch_receipts_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
                            
                            import zipfile
                            with zipfile.ZipFile(zip_path, 'w') as zipf:
                                for receipt in successful_receipts:
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
                        
                        if failed_receipts:
                            st.error(f"Failed to generate {len(failed_receipts)} receipts.")
                            st.dataframe(pd.DataFrame(failed_receipts))
            
            except Exception as e:
                st.error(f"Error processing batch file: {e}")
        
        # Show CSV template
        st.markdown("### CSV Template Format")
        st.markdown("Your CSV file should include the following columns:")
        
        csv_template = """
        receipt_number,receipt_date,customer_name,customer_address,description,amount,tax_rate,payment_method
        AIOLOS-202504-001,2025-04-29,Company A,"123 Main St, Athens",Consulting Services,1000,24,Bank Transfer
        AIOLOS-202504-002,2025-04-29,Company B,"456 Oak Ave, Heraklion",Property Management,2500,24,Credit Card
        """
        
        st.code(csv_template, language="csv")
        
        # Download template button
        csv_template_bytes = csv_template.strip().encode()
        st.download_button(
            label="Download CSV Template",
            data=csv_template_bytes,
            file_name="receipt_template.csv",
            mime="text/csv",
        )

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
