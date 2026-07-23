import tempfile
import os
import streamlit as st
from streamlit_chat import message

from main import (
    transcribe,
    load_embed_models,
    embed_texts,
    setup_qdrant,
    ingest,
    hybrid_search,
    setup_llm,
    COLLECTION_NAME,
)

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Chat with Audio ",
    page_icon="🎙️",
    layout="wide",
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }

    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    .main-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #8b949e;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    .status-ready {
        background: #1a4731; color: #3fb950;
        padding: 6px 14px; border-radius: 20px;
        font-size: 0.85rem; font-weight: 600; display: inline-block;
    }
    .status-idle {
        background: #2d1f00; color: #d29922;
        padding: 6px 14px; border-radius: 20px;
        font-size: 0.85rem; font-weight: 600; display: inline-block;
    }
    div[data-testid="stFileUploader"] {
        background-color: #161b22;
        border: 1px dashed #30363d;
        border-radius: 10px;
        padding: 0.5rem;
    }

    /* Push everything up so input bar doesn't overlap */
    .block-container { padding-bottom: 5rem !important; }

    /* Fix input bar to bottom */
    [data-testid="stBottom"] {
        position: fixed !important;
        bottom: 0 !important;
        background-color: #0e1117 !important;
        border-top: 1px solid #30363d !important;
        padding: 0.8rem 1rem !important;
        z-index: 999 !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "audio_ready" not in st.session_state:
    st.session_state.audio_ready = False
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "models_loaded" not in st.session_state:
    st.session_state.dense_model, st.session_state.sparse_model = load_embed_models()
    st.session_state.qdrant_client = setup_qdrant()
    st.session_state.llm = setup_llm()
    st.session_state.models_loaded = True

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎙️ Audio Upload")
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload an audio file",
        type=["mp3", "wav", "m4a", "ogg", "flac"],
        help="Supported: mp3, wav, m4a, ogg, flac"
    )

    if uploaded_file:
        st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")

        if st.button("🚀 Process Audio", use_container_width=True, type="primary"):
            with st.spinner("Transcribing audio..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                texts = transcribe(tmp_path)
                os.unlink(tmp_path)

            st.success(f"✅ Transcribed {len(texts)} segments")

            with st.spinner("Embedding & indexing..."):
                dense_emb, sparse_emb = embed_texts(
                    texts,
                    st.session_state.dense_model,
                    st.session_state.sparse_model
                )
                client = st.session_state.qdrant_client
                if client.collection_exists(COLLECTION_NAME):
                    client.delete_collection(COLLECTION_NAME)
                    st.session_state.qdrant_client = setup_qdrant()
                    client = st.session_state.qdrant_client
                ingest(client, texts, dense_emb, sparse_emb)

            st.session_state.messages = []
            st.session_state.audio_ready = True
            st.success("✅ Ready to chat!")

    st.markdown("---")

    if st.session_state.audio_ready:
        st.markdown('<span class="status-ready">● Audio Ready</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-idle">● No Audio Loaded</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("<small style='color:#8b949e'>Powered by Whisper · BGE · Qdrant · Ollama</small>", unsafe_allow_html=True)

# ─── MAIN AREA ────────────────────────────────────────────────────────────────

st.markdown('<div class="main-title">🎙️ Chat with Audio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Upload an audio file and ask anything about it</div>', unsafe_allow_html=True)
st.markdown("---")

# Chat history
if not st.session_state.messages:
    if st.session_state.audio_ready:
        st.markdown("<div style='text-align:center;color:#8b949e;margin-top:3rem'>Audio is ready! Ask your first question below 👇</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center;color:#8b949e;margin-top:3rem'>👈 Upload an audio file from the sidebar to get started</div>", unsafe_allow_html=True)
else:
    for i, msg in enumerate(st.session_state.messages):
        message(
            msg["content"],
            is_user=(msg["role"] == "user"),
            key=f"msg_{i}",
            avatar_style="micah" if msg["role"] == "user" else "avataaars",
        )

# ─── FIXED BOTTOM INPUT ───────────────────────────────────────────────────────

with st.container():
    col1, col2 = st.columns([8, 1])
    with col1:
        user_input = st.text_input(
            label="",
            placeholder="Ask something about the audio..." if st.session_state.audio_ready else "Upload and process an audio file first...",
            key=f"user_input_{st.session_state.input_key}",
            disabled=not st.session_state.audio_ready,
            label_visibility="collapsed",
        )
    with col2:
        send = st.button("Send ➤", type="primary", use_container_width=True, disabled=not st.session_state.audio_ready)

if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        contexts = hybrid_search(
            user_input,
            st.session_state.qdrant_client,
            st.session_state.dense_model,
            st.session_state.sparse_model
        )
        context_str = "\n\n---\n\n".join(contexts)
        prompt = (
            "Context information is below.\n"
            "---------------------\n"
            f"{context_str}\n"
            "---------------------\n"
            "Using the context above, answer the query in a crisp manner. "
            "If you don't know, say 'I don't know!'.\n"
            f"Query: {user_input}\n"
            "Answer: "
        )
        response = st.session_state.llm.stream_complete(prompt)
        full_response = "".join(chunk.delta for chunk in response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.input_key += 1  # clears the text input
    st.rerun()
