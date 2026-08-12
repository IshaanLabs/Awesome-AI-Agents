import streamlit as st
from main import get_ollama_models, get_llm, extract_topics, search_topics, generate_tweet

st.title("AI Tweet Generator")

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

    st.divider()
    st.header("Tavily")
    tavily_api_key = st.text_input("Tavily API Key", type="password")

# --- Main Area ---
user_text = st.text_area("What do you want to tweet about?", height=150, placeholder="e.g. The future of AI in healthcare is changing how doctors diagnose diseases...")

if st.button("Generate Tweet"):
    if not user_text.strip():
        st.warning("Please enter some text first.")
    elif not tavily_api_key.strip():
        st.warning("Please enter your Tavily API key in the sidebar.")
    elif not model_name:
        st.warning("Please select or enter a model name.")
    else:
        llm = get_llm(base_url, model_name)

        # Step 1 - Extract Topics
        print("Step 1: Extracting topics...")
        with st.spinner("Extracting key topics..."):
            topics = extract_topics(llm, user_text)
        st.subheader("Extracted Topics")
        st.write(", ".join([f"`{t}`" for t in topics]))

        # Step 2 - Web Search
        print("Step 2: Searching web...")
        with st.spinner("Searching the web for latest context..."):
            search_results = search_topics(tavily_api_key, topics)
        st.subheader("Web Search Results")
        for r in search_results:
            with st.expander(f"{r['topic']} — {r['title']}"):
                st.write(r["content"][:300])

        # Step 3 - Generate Tweet
        print("Step 3: Generating tweet...")
        with st.spinner("Generating viral tweet..."):
            tweet = generate_tweet(llm, user_text, topics, search_results)
        st.subheader("Generated Tweet")
        st.success(tweet)
        st.code(tweet, language="")
        print("Tweet displayed to user.")
