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
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    docs = [Document(page_content=chunk) for chunk in chunks]
    print(f"Total chunks: {len(docs)}")
    return docs


def split_docs(docs):
    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"Total chunks: {len(chunks)}")
    return chunks


def parse_questions(raw_text):
    print("Parsing questions from LLM output...")
    questions = []
    blocks = re.split(r"\n(?=Q\d+:)", raw_text.strip())
    for block in blocks:
        try:
            q_match = re.search(r"Q\d+:\s*(.+)", block)
            a_match = re.search(r"A\)\s*(.+)", block)
            b_match = re.search(r"B\)\s*(.+)", block)
            c_match = re.search(r"C\)\s*(.+)", block)
            d_match = re.search(r"D\)\s*(.+)", block)
            ans_match = re.search(r"Answer:\s*([ABCD])", block)

            if all([q_match, a_match, b_match, c_match, d_match, ans_match]):
                questions.append({
                    "question": q_match.group(1).strip(),
                    "options": {
                        "A": a_match.group(1).strip(),
                        "B": b_match.group(1).strip(),
                        "C": c_match.group(1).strip(),
                        "D": d_match.group(1).strip(),
                    },
                    "answer": ans_match.group(1).strip()
                })
        except Exception as e:
            print(f"Skipping block due to parse error: {e}")
    print(f"Parsed {len(questions)} question(s).")
    return questions


def generate_quiz(base_url, model_name, num_questions, text=None, file_path=None):
    print(f"Generating {num_questions} questions...")
    llm = get_llm(base_url, model_name)

    if file_path:
        docs = load_docs(file_path)
        chunks = split_docs(docs)
    else:
        chunks = split_text(text)

    prompt = PromptTemplate(
        input_variables=["text", "num_questions"],
        template="""You are a quiz generator. Based on the text below, generate exactly {num_questions} multiple choice questions.
        Each question must strictly follow this format:

        Q1: <question>
        A) <option>
        B) <option>
        C) <option>
        D) <option>
        Answer: <A/B/C/D>

        Text:
        {text}

        Generate {num_questions} questions now:"""
            )

    chain = prompt | llm
    all_questions = []

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunks)}...")
        raw = chain.invoke({"text": chunk.page_content, "num_questions": num_questions})
        print(f"Raw LLM output for chunk {i + 1}:\n{raw}")
        questions = parse_questions(raw)
        all_questions.extend(questions)

    print(f"Total questions generated: {len(all_questions)}")
    return all_questions


def format_txt_download(questions):
    print("Formatting questions for TXT download...")
    lines = []
    lines.append("=== QUIZ QUESTIONS ===\n")
    for i, q in enumerate(questions):
        lines.append(f"Q{i + 1}: {q['question']}")
        for key, val in q["options"].items():
            lines.append(f"  {key}) {val}")
        lines.append("")

    lines.append("\n=== ANSWERS ===\n")
    for i, q in enumerate(questions):
        lines.append(f"Q{i + 1}: {q['answer']}")

    print("TXT formatting complete.")
    return "\n".join(lines)
