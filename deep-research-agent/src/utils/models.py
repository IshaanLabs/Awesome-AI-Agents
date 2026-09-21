from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from src.utils.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TEMPERATURE

load_dotenv()

# default model for plain text responses (questions, answers, report writing)
llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=OLLAMA_MODEL,
    temperature=OLLAMA_TEMPERATURE,
)

# json model strictly for structured output calls
llm_json = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=OLLAMA_MODEL,
    temperature=OLLAMA_TEMPERATURE,
    format="json",
)
