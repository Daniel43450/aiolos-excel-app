import streamlit as st

# --- CONFIG ---
st.set_page_config(page_title="Aiolos Management", layout="wide")

# --- SESSION STATE INIT ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Dashboard"

# --- STYLE ---
st.markdown("""
    <style>
        .tab-bar {
            display: flex;
            justify-content: flex-start;
            border-bottom: 1px solid #ccc;
            margin-bottom: 2rem;
            gap: 6px;
        }

        .tab-btn {
            padding: 12px 20px;
            background-color: #f5f7fa;
            border: none;
            border-radius: 10px 10px 0 0;
            font-weight: 500;
            color: #0072b1;
            cursor: pointer;
            transition: 0.2s ease-in-out;
            font-size: 15px;
        }

        .tab-btn:hover {
            background-color: #e4e9f0;
        }

        .tab-btn.active {
            background-color: #00aaff;
            color: white !important;
            font-weight: bold;
            position: relative;
        }

        .tab-btn.active::after {
            content: "";
            position: absolute;
            bottom: 0;
            left: 20%;
            width: 60%;
            height: 4px;
            background-color: red;
            border-radius: 4px;
        }

        .tab-content {
            padding: 2rem;
            background-color: white;
            border-radius: 0 0 12px 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# --- TABS CONFIGURATION ---
tabs = {
    "Dashboard": "📊 Dashboard",
    "Ask": "💬 Ask Contamio",
    "Insights": "📈 Insights",
    "About": "ℹ️ About"
}

# --- RENDER TABS ---
st.markdown('<div class="tab-bar">', unsafe_allow_html=True)
for key, label in tabs.items():
    is_active = st.session_state.active_tab == key
    btn_class = "tab-btn active" if is_active else "tab-btn"
    if st.button(label, key=f"tab_{key}"):
        st.session_state.active_tab = key
    # Ghost button for styling structure (not clickable)
    st.markdown(f"<div class='{btn_class}' style='visibility:hidden;'>x</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- TAB CONTENT ---
st.markdown('<div class="tab-content">', unsafe_allow_html=True)

if st.session_state.active_tab == "Dashboard":
    st.subheader("📊 Dashboard")
    st.info("Main control center for your operations.")
    # 💡 your code here

elif st.session_state.active_tab == "Ask":
    st.subheader("💬 Ask Contamio")
    st.info("AI assistant for help and recommendations.")
    # 💡 your code here

elif st.session_state.active_tab == "Insights":
    st.subheader("📈 Insights")
    st.info("Data analysis and visual reports.")
    # 💡 your code here

elif st.session_state.active_tab == "About":
    st.subheader("ℹ️ About")
    st.info("Information about Aiolos system and features.")
    # 💡 your code here

st.markdown('</div>', unsafe_allow_html=True)
