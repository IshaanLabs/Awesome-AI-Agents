import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text-v2-moe:latest")
LLM_MODEL = os.getenv("LLM_MODEL", "codegemma:7b-instruct-v1.1-q4_K_S")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c", ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".env", ".sh"}


SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'chroma_db'}

def load_folder(path):
    print(f"\n[LOADER] Scanning folder: {path}")
    docs = []
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for file in filenames:
            ext = os.path.splitext(file)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                print(f"  [~] Ignored (unsupported type): {file}")
                continue
            filepath = os.path.join(dirpath, file)
            try:
                loader = TextLoader(filepath, encoding="utf-8")
                loaded = loader.load_and_split()
                docs.extend(loaded)
                print(f"  [+] Loaded: {filepath} ({len(loaded)} chunks)")
            except Exception as e:
                print(f"  [-] Skipped: {filepath} | Reason: {e}")
    print(f"\n[LOADER] Total documents loaded: {len(docs)}")
    return docs


def get_or_create_vectorstore(folder_path, embeddings):
    collection_name = os.path.basename(os.path.abspath(folder_path))
    persist_path = os.path.join(CHROMA_PERSIST_DIR, collection_name)

    if os.path.exists(persist_path):
        print(f"\n[CHROMA] Existing vectorstore found at: {persist_path}")
        print(f"[CHROMA] Loading persisted vectors — skipping re-processing...")
        db = Chroma(
            collection_name=collection_name,
            persist_directory=persist_path,
            embedding_function=embeddings
        )
        print(f"[CHROMA] Vectorstore loaded successfully.")
        return db

    print(f"\n[CHROMA] No existing vectorstore found. Creating new one at: {persist_path}")
    docs = load_folder(folder_path)

    print(f"\n[SPLITTER] Splitting documents into chunks...")
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = splitter.split_documents(docs)
    print(f"[SPLITTER] Total chunks after splitting: {len(texts)}")

    print(f"\n[CHROMA] Embedding and storing chunks — this may take a while...")
    db = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_path
    )
    print(f"[CHROMA] Vectorstore created and persisted at: {persist_path}")
    return db


def get_retriever(db):
    print(f"\n[RETRIEVER] Setting up retriever...")
    retriever = db.as_retriever(search_type="mmr", search_kwargs={"k": 10, "fetch_k": 50})
    print(f"[RETRIEVER] Retriever ready. Strategy: MMR | Top-K: 10 | Fetch-K: 50")
    return retriever


def generate_readme(retriever, output_path):
    print(f"\n[LLM] Initializing Ollama LLM: {LLM_MODEL}")
    llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.3)

    prompt_template = PromptTemplate.from_template("""
    You are an experienced software developer and technical writer.
    Analyze the following code context and generate a comprehensive README.md.

    The README must include:
    - Project Title and Description
    - Tech Stack (languages, frameworks, libraries used)
    - Project Structure (each file/module and its responsibility)
    - Installation (how to set up and install dependencies)
    - Usage (how to run the project with examples)
    - Configuration (any environment variables or config needed)

    Write in clean Markdown format. Be precise and technical.

    Code Context:
    {context}
    """)

    chain = prompt_template | llm | StrOutputParser()

    print(f"\n[LLM] Retrieving relevant code chunks...")
    docs = retriever.invoke("project structure files purpose dependencies configuration")
    context = "\n\n".join([d.page_content for d in docs])
    print(f"[LLM] Retrieved {len(docs)} chunks. Sending to {LLM_MODEL}...")
    print(f"[LLM] Generating README — please wait...\n")

    readme_content = chain.invoke({"context": context})

    print(f"\n[OUTPUT] Writing README.md to: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"[OUTPUT] README.md written successfully!")


if __name__ == "__main__":
    print("=" * 60)
    print("        README GENERATOR — Powered by Ollama + Chroma")
    print("=" * 60)

    folder_path = input("\nEnter the project folder path to scan: ").strip()

    if not os.path.exists(folder_path):
        print(f"\n[ERROR] Folder not found: {folder_path}")
        exit(1)

    print(f"\n[CONFIG] Embedding Model : {EMBED_MODEL}")
    print(f"[CONFIG] LLM Model       : {LLM_MODEL}")
    print(f"[CONFIG] Chroma DB Path  : {CHROMA_PERSIST_DIR}")
    print(f"[CONFIG] Ollama URL      : {OLLAMA_BASE_URL}")

    print(f"\n[EMBED] Initializing embedding model: {EMBED_MODEL}")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_BASE_URL)
    print(f"[EMBED] Embedding model ready.")

    db = get_or_create_vectorstore(folder_path, embeddings)
    retriever = get_retriever(db)

    output_readme = os.path.join(folder_path, "README.md")
    generate_readme(retriever, output_readme)

    print(f"\n{'=' * 60}")
    print(f"  Done! README.md saved at: {output_readme}")
    print(f"{'=' * 60}\n")
