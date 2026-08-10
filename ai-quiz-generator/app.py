import streamlit as st
import tempfile, os
from main import get_ollama_models, generate_quiz, format_txt_download

st.title("AI Quiz Generator")

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
        model_name = st.text_input("Or enter model name manually", value="llama3.2")

    num_questions = st.slider("Number of Questions per Chunk", min_value=1, max_value=20, value=5)

    st.divider()
    st.header("Input")
    input_mode = st.radio("Input Mode", ["Paste Text", "Upload File"])

# --- Input Area ---
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

# --- Generate Quiz ---
if st.button("Generate Quiz"):
    if input_mode == "Paste Text" and not (notes and notes.strip()):
        st.warning("Please paste some text first.")
    elif input_mode == "Upload File" and not file_path:
        st.warning("Please upload a PDF or TXT file.")
    elif not model_name:
        st.warning("Please select or enter a model name.")
    else:
        print(f"Generating quiz with model: {model_name}, num_questions: {num_questions}")
        with st.spinner("Generating quiz..."):
            questions = generate_quiz(base_url, model_name, num_questions, text=notes, file_path=file_path)
        if file_path:
            os.remove(file_path)
            print(f"Cleaned up temp file: {file_path}")
        st.session_state["questions"] = questions
        st.session_state["user_answers"] = {}
        st.session_state["submitted"] = False
        print(f"Quiz ready with {len(questions)} questions.")

# --- Quiz UI ---
if "questions" in st.session_state and st.session_state["questions"]:
    questions = st.session_state["questions"]

    if not st.session_state.get("submitted", False):
        st.subheader(f"Quiz — {len(questions)} Question(s)")
        with st.form("quiz_form"):
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i + 1}: {q['question']}**")
                options = [f"{k}) {v}" for k, v in q["options"].items()]
                choice = st.radio("", options, key=f"q_{i}", index=None)
                st.session_state["user_answers"][i] = choice
                st.divider()

            submitted = st.form_submit_button("Submit Quiz")
            if submitted:
                print("Quiz submitted by user.")
                st.session_state["submitted"] = True
                st.rerun()

    # --- Results Screen ---
    if st.session_state.get("submitted", False):
        st.subheader("Results")
        score = 0
        user_answers = st.session_state["user_answers"]

        for i, q in enumerate(questions):
            user_choice = user_answers.get(i)
            selected_key = user_choice[0] if user_choice else None
            correct = q["answer"]
            is_correct = selected_key == correct

            if is_correct:
                score += 1

            with st.expander(f"Q{i + 1}: {q['question']} — {'✅' if is_correct else '❌'}"):
                for key, val in q["options"].items():
                    if key == correct and key == selected_key:
                        st.markdown(f"**{key}) {val} ✅ (Your answer - Correct)**")
                    elif key == selected_key:
                        st.markdown(f"**{key}) {val} ❌ (Your answer - Wrong)**")
                    elif key == correct:
                        st.markdown(f"**{key}) {val} ✅ (Correct answer)**")
                    else:
                        st.write(f"{key}) {val}")

        st.success(f"Your Score: {score} / {len(questions)}")
        print(f"User scored: {score}/{len(questions)}")

        # --- TXT Download ---
        txt_content = format_txt_download(questions)
        st.download_button(
            label="Download Quiz as TXT",
            data=txt_content,
            file_name="quiz.txt",
            mime="text/plain"
        )
        print("TXT download button rendered.")

        if st.button("Retake Quiz"):
            print("User retaking quiz.")
            st.session_state["submitted"] = False
            st.session_state["user_answers"] = {}
            st.rerun()
