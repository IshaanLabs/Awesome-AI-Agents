import streamlit as st
from main import get_models, generate_text, get_prompt



def main():

    st.set_page_config(
        page_title="AI Grammar Checker",
        layout="wide"
    )

    st.title("📝 AI Grammar Checker")

    st.write("Correct grammar, spelling and writing using Ollama.")

    st.divider()

    # -----------------------------
    # Ollama URL
    # -----------------------------

    base_url = st.text_input(
        "Ollama URL",
        value="http://localhost:11434"
    )

    # -----------------------------
    # Load Models
    # -----------------------------

    if "models" not in st.session_state:
        st.session_state.models = get_models(base_url)

    if st.button("🔄 Refresh Models"):

        print("Refreshing models...")

        st.session_state.models = get_models(base_url)

    models = st.session_state.models

    # -----------------------------
    # Model Selection
    # -----------------------------

    if len(models) == 0:

        st.error("No models found.")

        return

    selected_model = st.selectbox(
        "Select Model",
        models
    )

    st.divider()

    # -----------------------------
    # User Input
    # -----------------------------

    user_text = st.text_area(
        "Enter your text",
        height=250
    )

    # -----------------------------
    # Generate
    # -----------------------------

    if st.button("✅ Correct Grammar"):

        if user_text.strip() == "":
            st.warning("Please enter some text.")
            return

        print("=" * 50)
        print("Selected Model:", selected_model)

        prompt = get_prompt(user_text)

        with st.spinner("Correcting..."):

            corrected_text = generate_text(
                base_url,
                selected_model,
                prompt
            )

        st.divider()

        st.subheader("Corrected Text")

        st.text_area(
            "",
            value=corrected_text,
            height=250
        )


if __name__ == "__main__":
    main()