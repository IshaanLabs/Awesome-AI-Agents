from langchain_ollama import OllamaLLM
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
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
    print("LLM loaded successfully.")
    return llm


def load_docs(file_path):
    print(f"Loading file: {file_path}")
    if file_path.endswith(".pdf"):
        print("Detected PDF file, using PyPDFLoader...")
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".txt"):
        print("Detected TXT file, using TextLoader...")
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF and TXT are supported.")
    docs = loader.load()
    print(f"Loaded {len(docs)} document(s) from file.")
    return docs


def split_docs(docs):
    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"Total chunks created: {len(chunks)}")
    return chunks


def split_text(text):
    print("Splitting raw text into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    docs = [Document(page_content=chunk) for chunk in chunks]
    print(f"Total chunks created: {len(docs)}")
    return docs


def summarize(base_url, model_name, text=None, file_path=None):
    print("Starting summarization...")
    llm = get_llm(base_url, model_name)

    if file_path:
        docs = load_docs(file_path)
        chunks = split_docs(docs)
    else:
        chunks = split_text(text)

    chain = load_summarize_chain(llm, chain_type="map_reduce", verbose=True)
    print("Running map-reduce chain...")
    result = chain.invoke(chunks)
    summary = result["output_text"]
    print("Summarization complete.")
    return summary
