import os
import tempfile
import streamlit as st
from main import load_resume, get_available_models, generate_cover_letter

st.set_page_config(page_title="AI Cover Letter Generator", page_icon="📝")
st.title("📝 AI Cover Letter Generator")

models = get_available_models()

if not models:
    st.error("Could not fetch models from Ollama. Check your OLLAMA_BASE_URL in .env")
    st.stop()

selected_model = st.selectbox("Select Ollama Model", models)

uploaded_pdf = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
job_description = st.text_area("Paste the Job Description", height=250)

if st.button("Generate Cover Letter"):
    if not uploaded_pdf:
        st.warning("Please upload your resume.")
    elif not job_description.strip():
        st.warning("Please enter the job description.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_pdf.read())
            tmp_path = tmp.name

        with st.spinner("Analysing resume, extracting relevant info, and generating cover letter..."):
            try:
                resume_text = load_resume(tmp_path)
                cover_letter = generate_cover_letter(resume_text, job_description, selected_model)
                st.success("Cover letter generated!")
                st.text_area("Your Cover Letter", value=cover_letter, height=400)
                st.download_button("Download Cover Letter", data=cover_letter, file_name="cover_letter.txt")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                os.unlink(tmp_path)
