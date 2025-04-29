import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="Aiolos App", layout="wide")

# --- CUSTOM STYLES ---
st.markdown("""
    <style>
        .stApp {
            background-color: #f8f9fa;
            font-family: 'Montserrat', sans-serif;
        }

        .tab-container {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 30px 0 10px;
        }

        .tab-button {
            padding: 12px 24px;
            border: none;
            background-color: #ddeeff;
            color: #003366;
            border-radius: 8px 8px 0 0;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease-in-out;
        }

        .tab-button:hover {
            background-color: #cce0ff;
        }

        .tab-button.active {
            background-color: #003366;
            color: white;
        }

        .decor-box {
            background-color: #eef5ff;
            border-left: 6px solid #003366;
            padding: 1.2em;
            margin: 1.5em 0;
            border-radius: 8px;
            font-size: 1em;
            color: #003366;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGO (OPTIONAL) ---
st.markdown("""
    <div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/Daniel43450/aiolos-excel-app/main/Capture.PNG" width="120">
    </div>
""", unsafe_allow_html=True)

# --- TOP TABS ---
tabs = {
    "Excel Processor": "📊 Excel Processor",
    "Receipt Generator": "🧾 Receipt Generator",
    "Receipt History": "📁 Receipt History"
}

# Active tab state
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Excel Processor"

# Render tabs as buttons
st.markdown('<div class="tab-container">', unsafe_allow_html=True)
for tab_key, tab_label in tabs.items():
    button_class = "tab-button active" if st.session_state.active_tab == tab_key else "tab-button"
    if st.button(tab_label, key=tab_key):
        st.session_state.active_tab = tab_key
st.markdown('</div>', unsafe_allow_html=True)

# --- TAB CONTENTS ---
if st.session_state.active_tab == "Excel Processor":
    st.title("📊 Excel Processor")
    st.markdown("""
        <div class="decor-box">
            Upload your Excel statement and get it automatically categorized.
        </div>
    """, unsafe_allow_html=True)
    # 👇 Fill here your Excel page code
    st.write("Excel Processor content goes here...")

elif st.session_state.active_tab == "Receipt Generator":
    st.title("🧾 Receipt Generator")
    st.markdown("""
        <div class="decor-box">
            Generate professional receipts from your DOCX template.
        </div>
    """, unsafe_allow_html=True)
    # 👇 Fill here your receipt generator code
    st.write("Receipt Generator content goes here...")

elif st.session_state.active_tab == "Receipt History":
    st.title("📁 Receipt History")
    st.markdown("""
        <div class="decor-box">
            View and download past generated receipts.
        </div>
    """, unsafe_allow_html=True)
    # 👇 Fill here your receipt history code
    st.write("Receipt History content goes here...")
