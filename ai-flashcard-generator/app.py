import streamlit as st
import tempfile, os, csv, io
from main import get_ollama_models, generate_flashcards

st.title("AI Flashcard Generator")

# --- Ollama Config ---
base_url = st.text_input("Ollama Base URL", value="http://localhost:11434")

if base_url:
    if st.button("Load Models"):
        print(f"Loading models from: {base_url}")
        models = get_ollama_models(base_url)
        st.session_state["models"] = models

if "models" in st.session_state and st.session_state["models"]:
    model_name = st.selectbox("Select Model", st.session_state["models"])
else:
    model_name = st.text_input("Or enter model name manually", value="llama3.2")

# --- Slider ---
num_cards = st.slider("Number of Flashcards per Chunk", min_value=1, max_value=20, value=5)

# --- Input Mode ---
input_mode = st.radio("Input Mode", ["Paste Text", "Upload File"])

notes = None
file_path = None

if input_mode == "Paste Text":
    notes = st.text_area("Paste your text here", height=300)
elif input_mode == "Upload File":
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
    if uploaded_file:
        suffix = ".pdf" if uploaded_file.type == "application/pdf" else ".txt"
        print(f"File uploaded: {uploaded_file.name}, suffix: {suffix}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            file_path = tmp.name
        print(f"Saved to temp path: {file_path}")

# --- Generate ---
if st.button("Generate Flashcards"):
    if input_mode == "Paste Text" and not (notes and notes.strip()):
        st.warning("Please paste some text first.")
    elif input_mode == "Upload File" and not file_path:
        st.warning("Please upload a PDF or TXT file.")
    elif not model_name:
        st.warning("Please select or enter a model name.")
    else:
        print(f"Generating flashcards with model: {model_name}, num_cards: {num_cards}")
        with st.spinner("Generating flashcards..."):
            flashcards = generate_flashcards(base_url, model_name, num_cards, text=notes, file_path=file_path)
        if file_path:
            os.remove(file_path)
            print(f"Cleaned up temp file: {file_path}")
        st.session_state["flashcards"] = flashcards

# --- Display Flashcards ---
if "flashcards" in st.session_state and st.session_state["flashcards"]:
    flashcards = st.session_state["flashcards"]
    st.subheader(f"Generated {len(flashcards)} Flashcard(s)")

    for i, card in enumerate(flashcards):
        with st.expander(f"Card {i + 1}: {card['question']}"):
            st.write(f"**Answer:** {card['answer']}")

    # --- CSV Download ---
    print("Preparing CSV download...")
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=["question", "answer"])
    writer.writeheader()
    writer.writerows(flashcards)
    st.download_button(
        label="Download Flashcards as CSV",
        data=csv_buffer.getvalue(),
        file_name="flashcards.csv",
        mime="text/csv"
    )
    print("CSV download button rendered.")
