import streamlit as st
from main import run

st.set_page_config(
    page_title="Website Summariser",
    page_icon="🌐",
    layout="wide"
)

st.markdown("""
    <style>
        .main { padding-top: 1.5rem; }
        .block-container { padding-left: 3rem; padding-right: 3rem; max-width: 100%; }

        .navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.8rem 0;
            border-bottom: 1px solid #e5e7eb;
            margin-bottom: 2rem;
        }
        .navbar-brand {
            font-size: 1.3rem;
            font-weight: 700;
            color: #4f46e5;
            letter-spacing: -0.5px;
        }
        .navbar-tag {
            background: #ede9fe;
            color: #4f46e5;
            border-radius: 999px;
            padding: 0.2rem 0.9rem;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .hero-title {
            font-size: 2.8rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.2;
            margin-bottom: 0.5rem;
        }
        .hero-title span { color: #6366f1; }
        .hero-sub {
            font-size: 1.05rem;
            color: #64748b;
            margin-bottom: 2rem;
            max-width: 600px;
        }
        .input-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.5rem 2rem;
            box-shadow: 0 1px 6px rgba(0,0,0,0.06);
            margin-bottom: 2rem;
        }
        .summary-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.8rem 2rem;
            box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        }
        .summary-text {
            color: #1e293b;
            font-size: 0.97rem;
            line-height: 1.8;
            white-space: pre-wrap;
        }
        .section-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #94a3b8;
            margin-bottom: 0.5rem;
        }
        .url-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: #f1f5f9;
            color: #475569;
            border-radius: 999px;
            padding: 0.3rem 1rem;
            font-size: 0.82rem;
            font-weight: 500;
            margin-bottom: 1.2rem;
            border: 1px solid #e2e8f0;
        }
        .stat-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 1rem 1.2rem;
            text-align: center;
        }
        .stat-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #4f46e5;
        }
        .stat-label {
            font-size: 0.75rem;
            color: #94a3b8;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stTextInput > div > div > input {
            border-radius: 8px;
            font-size: 0.95rem;
            border: 1px solid #cbd5e1;
            padding: 0.6rem 1rem;
        }
        .stButton > button {
            background: #6366f1;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.55rem 2rem;
            font-size: 0.95rem;
            font-weight: 600;
            width: 100%;
            transition: background 0.2s;
        }
        .stButton > button:hover { background: #4f46e5; color: white; }
        hr { border-color: #f1f5f9; }
    </style>
""", unsafe_allow_html=True)

# --- Navbar ---
st.markdown("""
    <div class="navbar">
        <div class="navbar-brand">🌐 WebSummariser</div>
        <div class="navbar-tag">Powered by Llama 3.2</div>
    </div>
""", unsafe_allow_html=True)

# --- Hero ---
col_hero, col_spacer = st.columns([2, 1])
with col_hero:
    st.markdown('<div class="hero-title">Summarise any<br><span>webpage instantly</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Paste a URL and get a clean AI-powered summary — scraped, cleaned, and summarised using Llama 3.2 running locally via Ollama.</div>', unsafe_allow_html=True)

st.markdown("---")

# --- Input Card ---
st.markdown('<div class="input-card">', unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])
with col_input:
    url = st.text_input("", placeholder="https://example.com/article", label_visibility="collapsed")
with col_btn:
    summarise_clicked = st.button("✨ Summarise")
st.markdown('</div>', unsafe_allow_html=True)

if summarise_clicked:
    if not url:
        st.warning("⚠️ Please enter a URL to continue.")
    elif not url.startswith("http"):
        st.warning("⚠️ URL should start with http:// or https://")
    else:
        with st.status("Analysing webpage...", expanded=True) as status:
            st.write("🔍 Scraping webpage...")
            try:
                st.write("🧹 Cleaning and extracting content...")
                st.write("🤖 Running map-reduce summarisation with Llama 3.2...")
                summary = run(url)
                status.update(label="✅ Summary ready!", state="complete", expanded=False)

                st.markdown("---")

                # --- Stats row ---
                word_count = len(summary.split())
                char_count = len(summary)
                bullet_count = summary.count("\n-") + summary.count("\n•") + summary.count("\n*")

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f'<div class="stat-box"><div class="stat-value">{word_count}</div><div class="stat-label">Words</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="stat-box"><div class="stat-value">{char_count}</div><div class="stat-label">Characters</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="stat-box"><div class="stat-value">{bullet_count}</div><div class="stat-label">Bullet Points</div></div>', unsafe_allow_html=True)
                with c4:
                    st.markdown(f'<div class="stat-box"><div class="stat-value">✓</div><div class="stat-label">Complete</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # --- Summary + Download side by side ---
                col_summary, col_actions = st.columns([3, 1])

                with col_summary:
                    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="url-pill">🔗 {url[:80]}{"..." if len(url) > 80 else ""}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="section-label">AI Summary</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="summary-text">{summary}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_actions:
                    st.markdown('<div class="section-label">Actions</div>', unsafe_allow_html=True)
                    st.download_button(
                        label="⬇️ Download Summary",
                        data=summary,
                        file_name="summary.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    st.text_area("📋 Copy Summary", value=summary, height=300)

            except Exception as e:
                status.update(label="❌ Failed", state="error", expanded=False)
                st.error(f"Something went wrong: {e}")

st.markdown("---")
st.markdown('<p style="text-align:center; color:#94a3b8; font-size:0.8rem;">Built with Streamlit · BeautifulSoup · Ollama Llama 3.2 &nbsp;|&nbsp; Runs 100% locally</p>', unsafe_allow_html=True)
