import streamlit as st
from main import run_agent

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Analyst Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark Professional Theme ───────────────────────────────────────────────────
st.markdown("""
<style>
    /* Base */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    /* Header */
    .app-header {
        padding: 1.5rem 0 0.5rem 0;
        border-bottom: 1px solid #30363d;
        margin-bottom: 1.5rem;
    }
    .app-header h1 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #58a6ff;
        margin: 0;
    }
    .app-header p {
        color: #8b949e;
        font-size: 0.9rem;
        margin: 0.3rem 0 0 0;
    }

    /* Cards */
    .card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .card-title {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8b949e;
        margin-bottom: 0.6rem;
    }

    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-green  { background: #1a3a2a; color: #3fb950; border: 1px solid #3fb950; }
    .badge-blue   { background: #1a2a3a; color: #58a6ff; border: 1px solid #58a6ff; }
    .badge-yellow { background: #3a2a1a; color: #d29922; border: 1px solid #d29922; }

    /* Response box */
    .response-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 3px solid #58a6ff;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
        color: #e0e0e0;
        line-height: 1.7;
    }

    /* Inputs */
    .stTextArea textarea {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: #e0e0e0 !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 2px rgba(88,166,255,0.15) !important;
    }

    /* Button */
    .stButton > button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background-color: #2ea043 !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #30363d;
        border-radius: 8px;
        overflow: hidden;
    }

    /* Sidebar labels */
    .sidebar-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8b949e;
        margin-bottom: 0.4rem;
    }

    /* Divider */
    hr { border-color: #30363d; }

    /* Hide default streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-label">Model</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="card" style="margin-bottom:1rem">
            <span class="badge badge-green">● Online</span>&nbsp;
            <span style="color:#e0e0e0; font-size:0.85rem; margin-left:0.4rem">Ollama (local)</span>
            <div style="margin-top:0.6rem; color:#8b949e; font-size:0.8rem">qwen2.5:7b-instruct-q4_K_M</div>
            <div style="color:#8b949e; font-size:0.8rem">localhost:11434</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Upload Data</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Upload CSV or Excel",
        label_visibility="collapsed",
        type=["csv", "xlsx"],
        help="Supported formats: CSV, Excel (.xlsx)",
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="color:#8b949e; font-size:0.75rem">Powered by LangChain + Ollama</div>', unsafe_allow_html=True)


# ── Main Area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>📊 Data Analyst Agent</h1>
    <p>Ask natural language questions about your data — powered by a local open-source LLM</p>
</div>
""", unsafe_allow_html=True)

if uploaded_file is None:
    st.markdown("""
    <div class="card" style="text-align:center; padding: 3rem 1.5rem;">
        <div style="font-size:2.5rem; margin-bottom:1rem">📂</div>
        <div style="color:#e0e0e0; font-size:1rem; font-weight:600">No file uploaded yet</div>
        <div style="color:#8b949e; font-size:0.85rem; margin-top:0.4rem">Upload a CSV or Excel file from the sidebar to get started</div>
    </div>
    """, unsafe_allow_html=True)

else:
    print(f"[APP] File uploaded: {uploaded_file.name}")

    # ── Data Preview ──────────────────────────────────────────────────────────
    from tools import preprocess_and_save
    temp_path, columns, df = preprocess_and_save(uploaded_file)

    if df is not None:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">Rows</div>
                <div style="font-size:1.6rem; font-weight:700; color:#58a6ff">{len(df):,}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">Columns</div>
                <div style="font-size:1.6rem; font-weight:700; color:#3fb950">{len(df.columns)}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">File</div>
                <div style="font-size:0.95rem; font-weight:600; color:#d29922; margin-top:0.3rem">{uploaded_file.name}</div>
            </div>""", unsafe_allow_html=True)

        # Data table
        st.markdown('<div class="card-title" style="margin-top:0.5rem">Data Preview</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=220)

        st.markdown('<div class="card-title">Columns</div>', unsafe_allow_html=True)
        st.markdown(
            " ".join([f'<span class="badge badge-blue">{c}</span>' for c in columns]),
            unsafe_allow_html=True,
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Query Section ─────────────────────────────────────────────────────
        st.markdown('<div class="card-title" style="margin-top:1rem">Ask a Question</div>', unsafe_allow_html=True)
        user_query = st.text_area(
            label="Query",
            label_visibility="collapsed",
            placeholder="e.g. What is the total sales by region? Which product has the highest revenue?",
            height=100,
        )

        submit = st.button("▶ Run Query", use_container_width=False)

        if submit:
            if not user_query.strip():
                st.warning("Please enter a query before submitting.")
            else:
                print(f"[APP] Query submitted: {user_query}")
                with st.spinner("🤖 Agent is thinking..."):
                    # Re-open file for run_agent since preprocess_and_save already read it
                    uploaded_file.seek(0)
                    answer = run_agent(uploaded_file, user_query)

                if answer:
                    st.markdown('<div class="card-title" style="margin-top:1.5rem">Response</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="response-box">{answer}</div>', unsafe_allow_html=True)
                    print(f"[APP] Response displayed successfully")
                else:
                    st.error("Agent returned no response. Check the terminal for details.")
