import html

import streamlit as st
import streamlit.components.v1 as components

from email_chain import generate_email, new_history


def copy_button(text, label="Copy email"):
    escaped = html.escape(text)
    components.html(
        f"""<button onclick="navigator.clipboard.writeText(document.getElementById('copy-target').innerText)"
        style="padding:0.4rem 1rem;cursor:pointer;">{label}</button>
        <pre id="copy-target" style="display:none">{escaped}</pre>""",
        height=45,
    )

st.set_page_config(page_title="AI Email Generator", layout="centered")
st.title("AI Email Generator")

if "history" not in st.session_state:
    st.session_state.history = new_history()
if "subject" not in st.session_state:
    st.session_state.subject = ""
if "body" not in st.session_state:
    st.session_state.body = ""
if "brief" not in st.session_state:
    st.session_state.brief = ""

description = st.text_area(
    "Describe the email you want",
    placeholder="e.g. Follow-up to a client about the Q3 proposal, friendly but professional tone...",
    height=120,
)

col1, col2 = st.columns(2)
with col1:
    generate_btn = st.button("Generate email", type="primary", use_container_width=True)
with col2:
    if st.button("New session", use_container_width=True):
        st.session_state.history = new_history()
        st.session_state.subject = ""
        st.session_state.body = ""
        st.session_state.brief = ""
        st.rerun()

if generate_btn:
    if not description.strip():
        st.warning("Describe the email first.")
    else:
        with st.spinner("Generating..."):
            st.session_state.brief = description.strip()
            subject, body = generate_email(st.session_state.brief, st.session_state.history)
            st.session_state.subject = subject
            st.session_state.body = body

if st.session_state.subject or st.session_state.body:
    st.subheader("Generated email")
    st.markdown(f"**Subject:** {st.session_state.subject}")
    st.text_area("Body", value=st.session_state.body, height=200, disabled=True, label_visibility="collapsed")

    full_email = f"Subject: {st.session_state.subject}\n\n{st.session_state.body}"
    copy_button(full_email)
    st.download_button("Download .txt", full_email, file_name="email.txt", mime="text/plain")

    st.divider()
    st.subheader("Want changes?")
    feedback = st.text_area(
        "Feedback",
        placeholder="e.g. Make it shorter, more formal, add a call to action...",
        height=80,
        label_visibility="collapsed",
    )
    if st.button("Apply feedback", type="primary"):
        if not feedback.strip():
            st.warning("Enter feedback first.")
        else:
            with st.spinner("Updating..."):
                subject, body = generate_email(
                    feedback.strip(),
                    st.session_state.history,
                    original_brief=st.session_state.brief,
                    prev_subject=st.session_state.subject,
                    prev_body=st.session_state.body,
                )
                st.session_state.subject = subject
                st.session_state.body = body
                st.rerun()
