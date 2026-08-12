from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from tavily import TavilyClient
import requests


def get_ollama_models(base_url):
    print(f"Fetching models from {base_url}...")
    try:
        response = requests.get(f"{base_url}/api/tags")
        response.raise_for_status()
        models = [model["name"] for model in response.json().get("models", [])]
        print(f"Found models: {models}")
        return models
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []


def get_llm(base_url, model_name):
    print(f"Loading LLM: {model_name} from {base_url}...")
    llm = OllamaLLM(model=model_name, base_url=base_url)
    print("LLM loaded.")
    return llm


def extract_topics(llm, user_text):
    print("Extracting key topics from user text...")
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Extract 3 to 5 key topics from the following text. 
        Return them as a comma-separated list only, no explanations.

        Text: {text}

        Key topics:"""
    )
    chain = prompt | llm
    result = chain.invoke({"text": user_text})
    topics = [t.strip() for t in result.strip().split(",") if t.strip()]
    print(f"Extracted topics: {topics}")
    return topics


def search_topics(tavily_api_key, topics):
    print(f"Searching web for topics: {topics}...")
    client = TavilyClient(api_key=tavily_api_key)
    search_results = []
    for topic in topics:
        print(f"Searching: {topic}")
        response = client.search(query=topic, max_results=3)
        for result in response.get("results", []):
            search_results.append({
                "topic": topic,
                "title": result.get("title", ""),
                "content": result.get("content", "")
            })
    print(f"Total search results: {len(search_results)}")
    return search_results


def generate_tweet(llm, user_text, topics, search_results):
    print("Generating tweet...")
    search_context = "\n".join(
        [f"- {r['title']}: {r['content'][:200]}" for r in search_results]
    )
    prompt = PromptTemplate(
        input_variables=["user_text", "topics", "search_context"],
        template="""You are a viral tweet writer. Using the user's idea, key topics and latest web context below, write one engaging and viral tweet.

            Rules:
            - Maximum 1000 characters
            - Include relevant hashtags at the end
            - Make it catchy, punchy and shareable
            - Do not include any explanation, just the tweet

            User idea: {user_text}
            Key topics: {topics}
            Latest web context:
            {search_context}

            Tweet:"""
    )
    chain = prompt | llm
    tweet = chain.invoke({
        "user_text": user_text,
        "topics": ", ".join(topics),
        "search_context": search_context
    }).strip()
    print(f"Generated tweet: {tweet}")
    return tweet
