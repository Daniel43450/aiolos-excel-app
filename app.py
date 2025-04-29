import streamlit as st

# --- CONFIG ---
st.set_page_config(page_title="Aiolos App", layout="wide")

# --- TABS HEADER STYLE ---
st.markdown("""
    <style>
        .stApp {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', sans-serif;
        }

        .tabs-wrapper {
            display: flex;
            justify-content: center;
            margin-top: 10px;
            border-bottom: 2px solid #dde3eb;
        }

        .tab {
            padding: 12px 28px;
            cursor: pointer;
            font-weight: 500;
            border: 1px solid transparent;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            margin: 0 5px;
            background-color: #e6ecf5;
            color: #003366;
            transition: all 0.2s ease;
        }

        .tab:hover {
            background-color: #d4e0f5;
        }

        .tab.selected {
            background-color: #003366;
            color: white;
            border-color: #003366 #003366 transparent #003366;
        }

        .page-title {
            color: #002244;
            font-size: 32px;
            margin-top: 10px;
            font-weight: 700;
            text-align: center;
        }

        .description-box {
            background-color: #eef4ff;
            border-left: 5px solid #003366;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 30px;
            color: #003366;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INIT ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Excel Processor"

# --- TOP TABS HTML ---
tab_labels = {
    "Excel Processor": "📊 Excel Processor",
    "Receipt Generator": "🧾 Receipt Generator",
    "Receipt History": "📁 Receipt History"
}

tabs_html = '<div class="tabs-wrapper">'
for key, label in tab_labels.items():
    selected_class = "selected" if st.session_state.active_tab == key else ""
    tabs_html += f"""
        <form action="" method="post">
            <button name="tab_button" value="{key}" class="tab {selected_class}">{label}</button>
        </form>
    """
tabs_html += "</div>"
st.markdown(tabs_html, unsafe_allow_html=True)

# --- HANDLE FORM SUBMIT ---
tab_button = st.experimental_get_query_params().get("tab_button", [None])[0]
if tab_button and tab_button in tab_labels:
    st.session_state.active_tab = tab_button

# --- TAB PAGES CONTENT ---
tab = st.session_state.active_tab

if tab == "Excel Processor":
    st.markdown('<div class="page-title">📊 Excel Processor</div>', unsafe_allow_html=True)
    st.markdown('<div class="description-box">Upload your Excel statement and get it categorized automatically.</div>', unsafe_allow_html=True)
    # 🔽 תכניס כאן את הקוד של עיבוד אקסל
    st.write("TODO: Excel processing page content here")

elif tab == "Receipt Generator":
    st.markdown('<div class="page-title">🧾 Receipt Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="description-box">Generate professional receipts from templates.</div>', unsafe_allow_html=True)
    # 🔽 תכניס כאן את הקוד של יצירת קבלות
    st.write("TODO: Receipt generation page content here")

elif tab == "Receipt History":
    st.markdown('<div class="page-title">📁 Receipt History</div>', unsafe_allow_html=True)
    st.markdown('<div class="description-box">View and download previously created receipts.</div>', unsafe_allow_html=True)
    # 🔽 תכניס כאן את הקוד של ההיסטוריה
    st.write("TODO: Receipt history page content here")
