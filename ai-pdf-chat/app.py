import streamlit as st
from streamlit_chat import message
from main import (get_ollama_models, load_documents, split_text_into_chunks,
                  create_embeddings, create_vector_store, load_llm,
                  create_chain, conversation_chat)
import os

st.markdown('<style>h1{color: orange; text-align: center;}</style>', unsafe_allow_html=True)
st.title("AI PDF Chat")
st.markdown('<style>h3{color: pink; text-align: center;}</style>', unsafe_allow_html=True)
st.subheader("Chat with your PDF documents 📄")

# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")

    base_url = st.text_input("Ollama Base URL", value="http://localhost:11434")

    if st.button("Load Models"):
        print(f"Loading models from: {base_url}")
        models = get_ollama_models(base_url)
        st.session_state["models"] = models

    if "models" in st.session_state and st.session_state["models"]:
        model_name = st.selectbox("Select Model", st.session_state["models"])
    else:
        model_name = st.text_input("Or enter model name manually", value="mistral:7b-instruct-q5_K_M")

    st.divider()
    st.header("Documents")

    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

    if st.button("Index Documents"):
        if not uploaded_files:
            st.warning("Please upload at least one PDF file.")
        else:
            print("Indexing documents...")
            with st.spinner("Indexing documents..."):
                documents, tmp_paths = load_documents(uploaded_files)
                text_chunks = split_text_into_chunks(documents)
                embeddings = create_embeddings(base_url)
                vector_store = create_vector_store(text_chunks, embeddings)
                llm = load_llm(base_url, model_name)
                chain = create_chain(llm, vector_store)
                st.session_state["chain"] = chain
                st.session_state["history"] = []
                st.session_state["generated"] = ["Hello! Ask me anything about your documents 🤗"]
                st.session_state["past"] = ["Hey! 👋"]
                for path in tmp_paths:
                    os.remove(path)
                    print(f"Cleaned up temp file: {path}")
            st.success(f"Indexed {len(uploaded_files)} file(s) successfully!")
            print("Indexing complete.")

    st.divider()
    if st.button("Clear Session"):
        print("Clearing session...")
        for key in ["chain", "history", "generated", "past", "models"]:
            if key in st.session_state:
                del st.session_state[key]
        st.success("Session cleared!")
        st.rerun()

# --- Initialize session state ---
if "generated" not in st.session_state:
    st.session_state["generated"] = ["Hello! Upload and index your PDFs to get started 🤗"]

if "past" not in st.session_state:
    st.session_state["past"] = ["Hey! 👋"]

if "history" not in st.session_state:
    st.session_state["history"] = []

# --- Chat UI ---
reply_container = st.container()
container = st.container()

with container:
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Question:", placeholder="Ask about your documents...", key="input")
        submit_button = st.form_submit_button(label="Send")

    if submit_button and user_input:
        if "chain" not in st.session_state:
            st.warning("Please upload and index your PDF documents first.")
        else:
            print(f"Sending query: {user_input}")
            output = conversation_chat(st.session_state["chain"], user_input, st.session_state["history"])
            st.session_state["past"].append(user_input)
            st.session_state["generated"].append(output)

if st.session_state["generated"]:
    with reply_container:
        for i in range(len(st.session_state["generated"])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user", avatar_style="thumbs")
            message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")
