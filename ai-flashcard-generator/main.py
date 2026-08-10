from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import requests
import re


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
        print("Detected PDF, using PyPDFLoader...")
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".txt"):
        print("Detected TXT, using TextLoader...")
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF and TXT are supported.")
    docs = loader.load()
    print(f"Loaded {len(docs)} document(s).")
    return docs


def split_text(text):
    print("Splitting raw text into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
    chunks = splitter.split_text(text)
    docs = [Document(page_content=chunk) for chunk in chunks]
    print(f"Total chunks: {len(docs)}")
    return docs


def split_docs(docs):
    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    print(f"Total chunks: {len(chunks)}")
    return chunks


def parse_flashcards(raw_text):
    print("Parsing flashcards from LLM output...")
    flashcards = []
    pattern = r"Q:\s*(.+?)\s*A:\s*(.+?)(?=Q:|$)"
    matches = re.findall(pattern, raw_text, re.DOTALL)
    for q, a in matches:
        flashcards.append({"question": q.strip(), "answer": a.strip()})
    print(f"Parsed {len(flashcards)} flashcard(s).")
    return flashcards


def generate_flashcards(base_url, model_name, num_cards, text=None, file_path=None):
    print(f"Generating {num_cards} flashcards...")
    llm = get_llm(base_url, model_name)

    if file_path:
        docs = load_docs(file_path)
        chunks = split_docs(docs)
    else:
        chunks = split_text(text)

    prompt = PromptTemplate(
        input_variables=["text", "num_cards"],
        template="""You are a flashcard generator. Based on the text below, generate exactly {num_cards} flashcards.
        Each flashcard must follow this exact format:
        Q: <question>
        A: <answer>

        Text:
        {text}

        Generate {num_cards} flashcards now:"""
            )

    chain = prompt | llm

    all_flashcards = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunks)}...")
        raw = chain.invoke({"text": chunk.page_content, "num_cards": num_cards})
        print(f"Raw LLM output for chunk {i + 1}:\n{raw}")
        cards = parse_flashcards(raw)
        all_flashcards.extend(cards)

    print(f"Total flashcards generated: {len(all_flashcards)}")
    return all_flashcards
