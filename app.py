import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(page_title="Aiolos App", layout="wide")

# --- STATE INIT ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Excel Processor"

# --- ADVANCED STYLES ---
st.markdown("""
    <style>
        .tabs-container {
            display: flex;
            justify-content: center;
            margin: 2rem 0 1rem 0;
        }

        .tab-button {
            padding: 14px 28px;
            margin: 0 6px;
            border: none;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            background-color: #e2e8f0;
            color: #003366;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease-in-out;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .tab-button:hover {
            background-color: #cbdcf5;
        }

        .tab-button.active {
            background-color: #003366 !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .tab-content {
            background-color: #ffffff;
            border-radius: 0 0 12px 12px;
            padding: 2rem 2rem 3rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            margin-top: -8px;
        }

        .tab-divider {
            border-bottom: 2px solid #e5e7eb;
            margin-bottom: 0;
        }
    </style>
""", unsafe_allow_html=True)

# --- TABS HEADER ---
tabs = ["Excel Processor", "Receipt Generator", "Receipt History"]

st.markdown('<div class="tabs-container">', unsafe_allow_html=True)
for tab in tabs:
    is_active = st.session_state.active_tab == tab
    btn_class = "tab-button active" if is_active else "tab-button"
    st.markdown(
        f'<button class="{btn_class}" onclick="window.location.search=\'?tab={tab}\'">{tab}</button>',
        unsafe_allow_html=True
    )
st.markdown('</div><div class="tab-divider"></div>', unsafe_allow_html=True)

# --- HANDLE CLICK USING QUERY PARAMS ---
query_tab = st.query_params.get("tab")
if query_tab in tabs:
    st.session_state.active_tab = query_tab

# --- TAB CONTENT ---
tab = st.session_state.active_tab
st.markdown('<div class="tab-content">', unsafe_allow_html=True)

if tab == "Excel Processor":
    st.subheader("📊 Excel Processor")
    st.info("Upload an Excel file and automatically categorize the rows.")
    # 🔽 put your Excel logic here

elif tab == "Receipt Generator":
    st.subheader("🧾 Receipt Generator")
    st.info("Upload a DOCX template and fill receipt details to generate.")
    # 🔽 put your receipt generator logic here

elif tab == "Receipt History":
    st.subheader("📁 Receipt History")
    st.info("Browse and download previously generated receipts.")
    # 🔽 put your receipt history logic here

st.markdown('</div>', unsafe_allow_html=True)
