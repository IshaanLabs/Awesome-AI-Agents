# README Generator — Powered by Ollama + ChromaDB

An LLM-based CLI tool that automatically scans a local project folder, embeds the source code into a vector store, and generates a comprehensive `README.md` using a fully local Ollama model — no API keys, no cloud dependency.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core language |
| LangChain | Orchestration (document loading, splitting, chaining) |
| langchain-ollama | Ollama LLM + Embeddings integration |
| langchain-community | TextLoader, ChromaDB vectorstore wrapper |
| ChromaDB | Local persistent vector database |
| Ollama | Local LLM inference server |
| python-dotenv | Environment variable management |

**Models used:**
- Embedding: `nomic-embed-text-v2-moe:latest`
- LLM: `codegemma:7b-instruct-v1.1-q4_K_S`

---

## Project Structure

```
readme/
├── main.py           # Core logic — all functions and entry point
├── .env              # Configuration (models, URLs, paths)
├── requirements.txt  # Python dependencies
└── chroma_db/        # Auto-created — persisted vector embeddings per project
```

### Functions in `main.py`

| Function | Responsibility |
|---|---|
| `load_folder(path)` | Walks the project directory, loads supported file types, skips binaries and system folders |
| `get_or_create_vectorstore()` | Loads existing ChromaDB if present, otherwise embeds and persists new vectors |
| `get_retriever(db)` | Sets up MMR-based retriever from ChromaDB |
| `generate_readme()` | Retrieves relevant code chunks, builds prompt, invokes LLM, writes `README.md` |

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd readme
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Make sure [Ollama](https://ollama.com) is running and the required models are pulled:
   ```bash
   ollama pull nomic-embed-text-v2-moe:latest
   ollama pull codegemma:7b-instruct-v1.1-q4_K_S
   ```

---

## Configuration

Create a `.env` file in the project root:

```env
OLLAMA_BASE_URL=http://localhost:11434
EMBED_MODEL=nomic-embed-text-v2-moe:latest
LLM_MODEL=codegemma:7b-instruct-v1.1-q4_K_S
CHROMA_PERSIST_DIR=./chroma_db
```

| Variable | Description |
|---|---|
| `OLLAMA_BASE_URL` | Ollama server URL (local or remote) |
| `EMBED_MODEL` | Model used to embed code chunks |
| `LLM_MODEL` | Model used to generate the README |
| `CHROMA_PERSIST_DIR` | Directory where ChromaDB vectors are stored |

---

## Usage

```bash
python main.py
```

You will be prompted to enter the path of the project folder to scan:

```
Enter the project folder path to scan: ./my_project
```

The tool will:
1. Scan all supported files in the folder (skipping `.git`, `venv`, `__pycache__` etc.)
2. Embed and store chunks in ChromaDB (skipped on subsequent runs for the same folder)
3. Retrieve the most relevant code chunks using MMR search
4. Send the context to the LLM and generate a `README.md`
5. Save `README.md` directly inside the scanned project folder

---

## Supported File Types

`.py` `.js` `.ts` `.java` `.go` `.rs` `.cpp` `.c` `.md` `.txt` `.yaml` `.yml` `.json` `.toml` `.env` `.sh`

---

## Notes

- On the **first run** for a project, embeddings are computed and persisted to `chroma_db/<project_name>/`
- On **subsequent runs**, the persisted vectors are reloaded — no re-embedding needed
- To force re-indexing, delete the corresponding folder inside `chroma_db/`
