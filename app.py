import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="Aiolos Management System", layout="wide")

# --- STATE INIT ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Excel Processor"

# --- CUSTOM STYLE ---
st.markdown("""
    <style>
        /* GENERAL APP STYLE */
        .stApp {
            background-color: #f4f7fb;
            font-family: 'Segoe UI', sans-serif;
        }

        /* TABS STYLE */
        .tabs-container {
            display: flex;
            justify-content: center;
            margin-top: 30px;
        }

        .tab-button {
            padding: 14px 30px;
            margin: 0 8px;
            border: none;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            background-color: #dde6f0;
            color: #003366;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.25s ease;
        }

        .tab-button:hover {
            background-color: #c7d9f5;
        }

        .tab-button.active {
            background-color: #003366;
            color: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        .tab-content {
            background-color: white;
            padding: 2.5rem 2rem;
            border-radius: 0 0 12px 12px;
            margin-top: -4px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.05);
        }

        .tab-divider {
            border-bottom: 2px solid #e1e7ee;
            margin-bottom: 0;
        }

        .logo-container {
            text-align: center;
            margin-top: 15px;
        }

        .logo-container img {
            width: 100px;
            border-radius: 50%;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGO ---
st.markdown("""
    <div class="logo-container">
        <img src="https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG" alt="Aiolos Logo">
    </div>
""", unsafe_allow_html=True)

# --- TABS DEFINITION ---
tabs = ["Excel Processor", "Receipt Generator", "Receipt History"]

# --- TABS DISPLAY ---
st.markdown('<div class="tabs-container">', unsafe_allow_html=True)
for tab in tabs:
    active = st.session_state.active_tab == tab
    btn_class = "tab-button active" if active else "tab-button"
    if st.button(tab, key=tab):
        st.session_state.active_tab = tab
    st.markdown(f"<div class='{btn_class}' style='visibility:hidden;'>x</div>", unsafe_allow_html=True)  # spacer for layout
st.markdown('</div><div class="tab-divider"></div>', unsafe_allow_html=True)

# --- TAB CONTENT AREA ---
st.markdown('<div class="tab-content">', unsafe_allow_html=True)

if st.session_state.active_tab == "Excel Processor":
    st.subheader("📊 Excel Processor")
    st.info("Upload your bank Excel/CSV statements to get categorized output.")
    # ✏️ Place your Excel processing code here

elif st.session_state.active_tab == "Receipt Generator":
    st.subheader("🧾 Receipt Generator")
    st.info("Upload a DOCX template and fill in receipt details.")
    # ✏️ Place your receipt generation code here

elif st.session_state.active_tab == "Receipt History":
    st.subheader("📁 Receipt History")
    st.info("View, search and download your previous receipts.")
    # ✏️ Place your receipt history code here

st.markdown('</div>', unsafe_allow_html=True)
