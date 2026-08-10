import streamlit as st
import tempfile, os
from main import get_ollama_models, summarize

st.title("AI Notes Summarizer")

base_url = st.text_input("Ollama Base URL", value="http://localhost:11434")

models = []
if base_url:
    if st.button("Load Models"):
        print(f"User requested models from: {base_url}")
        models = get_ollama_models(base_url)
        st.session_state["models"] = models

if "models" in st.session_state and st.session_state["models"]:
    model_name = st.selectbox("Select Model", st.session_state["models"])
else:
    model_name = st.text_input("Or enter model name manually", value="llama3.2")

input_mode = st.radio("Input Mode", ["Paste Text", "Upload File"])

notes = None
file_path = None

if input_mode == "Paste Text":
    notes = st.text_area("Paste your notes here", height=300)
elif input_mode == "Upload File":
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
    if uploaded_file:
        suffix = ".pdf" if uploaded_file.type == "application/pdf" else ".txt"
        print(f"File uploaded: {uploaded_file.name}, type: {suffix}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            file_path = tmp.name
        print(f"Saved uploaded file to temp path: {file_path}")

if st.button("Summarize"):
    if input_mode == "Paste Text" and not (notes and notes.strip()):
        st.warning("Please paste some notes first.")
    elif input_mode == "Upload File" and not file_path:
        st.warning("Please upload a PDF or TXT file.")
    elif not model_name:
        st.warning("Please select or enter a model name.")
    else:
        print(f"Summarizing with model: {model_name}, base_url: {base_url}")
        with st.spinner("Summarizing..."):
            summary = summarize(base_url, model_name, text=notes, file_path=file_path)
        if file_path:
            os.remove(file_path)
            print(f"Cleaned up temp file: {file_path}")
        print("Summary displayed to user.")
        st.subheader("Summary")
        st.write(summary)
