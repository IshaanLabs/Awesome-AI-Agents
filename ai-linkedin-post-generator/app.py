import streamlit as st
from main import generate_linkedin_post

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI LinkedIn Post Generator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Global CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
        /* hide streamlit default chrome */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* full page padding */
        .block-container {
            padding-top: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
            max-width: 100%;
        }

        /* app header bar */
        .app-header {
            background: linear-gradient(90deg, #0077B5, #00A0DC);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            color: white;
        }
        .app-header h1 {
            margin: 0;
            font-size: 1.8rem;
            font-weight: 700;
            color: white;
        }
        .app-header p {
            margin: 0.3rem 0 0 0;
            font-size: 0.95rem;
            opacity: 0.85;
            color: white;
        }

        /* section card */
        .section-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        /* output card */
        .output-card {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-left: 4px solid #0077B5;
            border-radius: 12px;
            padding: 1.5rem;
            height: 100%;
        }

        /* section label */
        .section-label {
            font-size: 0.8rem;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
        }

        /* primary button override */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #0077B5, #00A0DC);
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1rem;
            padding: 0.6rem 1.2rem;
            color: white;
            transition: opacity 0.2s ease;
        }
        div.stButton > button[kind="primary"]:hover {
            opacity: 0.9;
        }

        /* text area styling */
        textarea {
            border-radius: 8px !important;
            font-size: 0.95rem !important;
            line-height: 1.6 !important;
        }

        /* input styling */
        input[type="text"] {
            border-radius: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
    <div class="app-header">
        <h1>✍️ AI LinkedIn Post Generator</h1>
        <p>Powered by Ollama (gemma3) + Exa Search — 100% open source, runs locally.</p>
    </div>
""", unsafe_allow_html=True)

# ─── Two Column Layout ───────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

# ════════════════════════════════════════════════════════════
# LEFT COLUMN — Inputs
# ════════════════════════════════════════════════════════════
with left_col:
    st.markdown('<div class="section-label">⚙️ Post Configuration</div>', unsafe_allow_html=True)

    keywords = st.text_input(
        "🔑 Keywords",
        placeholder="e.g., AI Guardrails, Remote Work, Python Tips...",
        help="Keywords that define the topic of your LinkedIn post."
    )

    user_description = st.text_area(
        "💬 What do you want to post about?",
        placeholder="e.g., I want to write about how startups use AI guardrails to prevent agent misbehavior in production environments...",
        height=130,
        help="Optional but highly recommended — gives the AI more context for a focused, relevant post."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        post_type = st.selectbox(
            "📌 Post Type",
            ["General", "How-to Guide", "Listicle", "Poll", "FAQs", "Job Post", "Checklist", "Reality Check"],
            help="Format that fits your message."
        )
    with col2:
        post_length = st.selectbox(
            "📏 Length",
            ["Short (150-300 words)", "Medium (300-600 words)", "Long (600-1000 words)"],
            help="How long should the post be."
        )
    with col3:
        language = st.selectbox(
            "🌐 Language",
            ["English", "Hindi", "Spanish", "Vietnamese", "Chinese"],
            help="Language for your audience."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    generate_clicked = st.button("🚀 Generate LinkedIn Post", use_container_width=True, type="primary")

# ════════════════════════════════════════════════════════════
# RIGHT COLUMN — Output
# ════════════════════════════════════════════════════════════
with right_col:
    st.markdown('<div class="section-label">📄 Generated Post</div>', unsafe_allow_html=True)

    # ─── Handle generation ───────────────────────────────────
    if generate_clicked:
        if not keywords.strip():
            st.error("⚠️ Please enter some keywords before generating!")
        else:
            with st.spinner("🔍 Searching the web + 🤖 Generating your post..."):
                post = generate_linkedin_post(keywords, post_type, post_length, language, user_description)

            if post:
                st.session_state["generated_post"] = post
            else:
                st.error("❌ Post generation failed. Check terminal for details.")
                st.warning("🔍 Exa search likely failed — no post generated to avoid hallucination.")
                st.info("💡 Check EXA_API_KEY in .env and make sure Ollama is running.")

    # ─── Show output if available ────────────────────────────
    if "generated_post" in st.session_state and st.session_state["generated_post"]:
        st.success("✅ Your LinkedIn post is ready!")
        st.text_area(
            "Generated LinkedIn Post",
            value=st.session_state["generated_post"],
            height=480,
            label_visibility="hidden"
        )
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.write(
                f"""<script>navigator.clipboard.writeText(`{st.session_state["generated_post"]}`)</script>""",
                unsafe_allow_html=True
            )
            st.success("✅ Copied!")
    else:
        # placeholder when no post is generated yet
        st.markdown("""
            <div style="
                height: 480px;
                border: 2px dashed #d1d5db;
                border-radius: 12px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: #9ca3af;
                font-size: 1rem;
                text-align: center;
                padding: 2rem;
            ">
                <div style="font-size: 3rem;">✍️</div>
                <div style="margin-top: 1rem; font-weight: 600;">Your post will appear here</div>
                <div style="margin-top: 0.5rem; font-size: 0.85rem;">Fill in the settings on the left and click Generate</div>
            </div>
        """, unsafe_allow_html=True)
