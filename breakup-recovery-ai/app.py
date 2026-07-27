import os
import tempfile

import streamlit as st

from main import run_graph

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="💔 Breakup Recovery Squad",
    page_icon="💔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Base */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0f0f0f;
        color: #f0e6d3;
        font-family: 'Georgia', serif;
    }

    [data-testid="stHeader"] { background: transparent; }

    /* Hero */
    .hero {
        text-align: center;
        padding: 2.5rem 1rem 1rem;
    }
    .hero h1 {
        font-size: 3rem;
        background: linear-gradient(135deg, #e07b8a, #c9a96e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .hero p {
        color: #a89080;
        font-size: 1.05rem;
        margin-top: 0;
    }

    /* Cards */
    .card {
        background: #1a1a1a;
        border: 1px solid #2e2e2e;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Section labels */
    .section-label {
        font-size: 0.78rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #c9a96e;
        margin-bottom: 0.4rem;
    }

    /* Textarea override */
    textarea {
        background-color: #141414 !important;
        color: #f0e6d3 !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
    }
    textarea:focus { border-color: #e07b8a !important; }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #141414;
        border: 1px dashed #3a3a3a;
        border-radius: 10px;
        padding: 0.5rem;
    }

    /* Primary button */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #e07b8a, #c9506a);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 2.5rem;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        transition: opacity 0.2s;
        width: 100%;
    }
    div.stButton > button[kind="primary"]:hover { opacity: 0.88; }

    /* Tabs */
    [data-testid="stTabs"] button {
        color: #a89080 !important;
        font-size: 0.9rem;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #e07b8a !important;
        border-bottom: 2px solid #e07b8a !important;
    }

    /* Result cards */
    .result-card {
        background: #161616;
        border-left: 3px solid #e07b8a;
        border-radius: 0 12px 12px 0;
        padding: 1.4rem 1.6rem;
        margin-top: 0.5rem;
        line-height: 1.75;
    }
    .result-card.closure  { border-left-color: #c9a96e; }
    .result-card.routine  { border-left-color: #7ec8a4; }
    .result-card.honesty  { border-left-color: #9b8ec4; }

    /* Status badge */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.06em;
    }
    .badge-done { background: #1e3a2f; color: #7ec8a4; }
    .badge-wait { background: #2a2a1e; color: #c9a96e; }

    /* Divider */
    hr { border-color: #2a2a2a; }

    /* Image preview */
    .img-preview { border-radius: 10px; border: 1px solid #2e2e2e; }

    /* Footer */
    .footer {
        text-align: center;
        color: #4a4a4a;
        font-size: 0.8rem;
        padding: 2rem 0 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_uploaded_files(files) -> list[str]:
    paths = []
    for f in files:
        try:
            tmp = os.path.join(tempfile.gettempdir(), f"brs_{f.name}")
            with open(tmp, "wb") as fp:
                fp.write(f.getvalue())
            paths.append(tmp)
            print(f"[app] Saved uploaded file to {tmp}")
        except Exception as e:
            print(f"[app] ERROR - Failed to save {f.name}: {e}")
    return paths


def render_result_tab(content: str, accent_class: str):
    st.markdown(f'<div class="result-card {accent_class}">', unsafe_allow_html=True)
    st.markdown(content)
    st.markdown("</div>", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>💔 Breakup Recovery Squad</h1>
    <p>Your AI-powered team to help you heal, find closure, and move forward.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Input Section ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown('<p class="section-label">💬 Your Story</p>', unsafe_allow_html=True)
    user_input = st.text_area(
        label="feelings",
        label_visibility="collapsed",
        placeholder="Tell us what happened... How are you feeling right now?",
        height=200,
    )

with col_right:
    st.markdown('<p class="section-label">🖼️ Chat Screenshots (optional)</p>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        label="screenshots",
        label_visibility="collapsed",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="screenshots",
    )
    if uploaded_files:
        img_cols = st.columns(min(len(uploaded_files), 3))
        for i, f in enumerate(uploaded_files):
            with img_cols[i % 3]:
                st.image(f, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Submit ────────────────────────────────────────────────────────────────────
_, btn_col, _ = st.columns([2, 2, 2])
with btn_col:
    submit = st.button("Get My Recovery Plan 💝", type="primary")

st.markdown("---")

# ── Processing & Results ──────────────────────────────────────────────────────
if submit:
    if not user_input and not uploaded_files:
        st.warning("Please share your feelings or upload a screenshot before continuing.")
    else:
        print("[app] User submitted — starting graph run")

        image_paths = save_uploaded_files(uploaded_files) if uploaded_files else []

        # Progress bar
        progress = st.progress(0, text="Starting your recovery plan...")

        STEPS = [
            (25,  "🤗 Getting empathetic support..."),
            (50,  "✍️  Crafting closure messages..."),
            (75,  "📅  Building your 7-day plan..."),
            (100, "💪  Gathering honest perspective..."),
        ]

        # Run graph with live progress updates using placeholders
        result      = None
        status_slot = st.empty()

        try:
            # We run the graph and update progress step-by-step via streaming nodes
            from main import build_graph, RecoveryState

            initial_state: RecoveryState = {
                "user_text":     user_input or "",
                "image_paths":   image_paths,
                "therapist_out": "",
                "closure_out":   "",
                "routine_out":   "",
                "honesty_out":   "",
            }

            graph = build_graph()

            step_map = {
                "therapist": (25,  "🤗 Therapist is listening..."),
                "closure":   (50,  "✍️  Writing closure messages..."),
                "routine":   (75,  "📅  Planning your recovery week..."),
                "honesty":   (100, "💪  Delivering honest feedback..."),
            }

            result = initial_state.copy()
            for event in graph.stream(initial_state):
                for node_name, node_output in event.items():
                    pct, msg = step_map.get(node_name, (100, "Finishing up..."))
                    progress.progress(pct, text=msg)
                    result.update(node_output)
                    print(f"[app] Node '{node_name}' streamed result")

        except Exception as e:
            print(f"[app] ERROR - Graph run failed: {e}")
            st.error(f"Something went wrong: {e}")
            st.stop()

        progress.empty()
        status_slot.empty()

        # ── Results Tabs ──────────────────────────────────────────────────────
        st.markdown("### 🌿 Your Personalized Recovery Plan")
        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs([
            "🤗 Emotional Support",
            "✍️ Find Closure",
            "📅 Recovery Plan",
            "💪 Honest Perspective",
        ])

        with tab1:
            render_result_tab(result.get("therapist_out", ""), "")

        with tab2:
            render_result_tab(result.get("closure_out", ""), "closure")

        with tab3:
            render_result_tab(result.get("routine_out", ""), "routine")

        with tab4:
            render_result_tab(result.get("honesty_out", ""), "honesty")

        print("[app] Results rendered successfully")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Made with ❤️ · Breakup Recovery Squad · #BreakupRecoverySquad
</div>
""", unsafe_allow_html=True)
