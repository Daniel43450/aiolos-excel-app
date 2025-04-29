import streamlit as st

# --- CONFIG ---
st.set_page_config(page_title="Aiolos App", layout="wide")

# --- STATE INIT ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Excel Processor"

# --- STYLE ---
st.markdown("""
    <style>
        .tab-btn {
            border: none;
            padding: 12px 24px;
            border-radius: 10px 10px 0 0;
            font-weight: 600;
            margin-right: 5px;
            background-color: #ddeeff;
            color: #003366;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .tab-btn:hover {
            background-color: #cce0ff;
        }
        .tab-btn-selected {
            background-color: #003366 !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- TABS USING COLUMNS ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Excel Processor", key="tab1"):
        st.session_state.active_tab = "Excel Processor"
    st.markdown(f"<button class='tab-btn {'tab-btn-selected' if st.session_state.active_tab == 'Excel Processor' else ''}' disabled> </button>", unsafe_allow_html=True)

with col2:
    if st.button("🧾 Receipt Generator", key="tab2"):
        st.session_state.active_tab = "Receipt Generator"
    st.markdown(f"<button class='tab-btn {'tab-btn-selected' if st.session_state.active_tab == 'Receipt Generator' else ''}' disabled> </button>", unsafe_allow_html=True)

with col3:
    if st.button("📁 Receipt History", key="tab3"):
        st.session_state.active_tab = "Receipt History"
    st.markdown(f"<button class='tab-btn {'tab-btn-selected' if st.session_state.active_tab == 'Receipt History' else ''}' disabled> </button>", unsafe_allow_html=True)

# --- CONTENT ---
tab = st.session_state.active_tab

if tab == "Excel Processor":
    st.title("📊 Excel Processor")
    st.info("Upload your Excel and get categorized output.")
    # 👇 Excel logic goes here

elif tab == "Receipt Generator":
    st.title("🧾 Receipt Generator")
    st.info("Upload template and generate receipt.")
    # 👇 Generator logic here

elif tab == "Receipt History":
    st.title("📁 Receipt History")
    st.info("View, download, and search receipts.")
    # 👇 History logic here
