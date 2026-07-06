# 🎙️ Voice2Tasks

Transform voice memos into structured tasks, Kanban boards, and downloadable todo lists. Powered by Whisper for transcription, LangChain + Ollama for intelligent task extraction, and ChromaDB for RAG-based querying over past memos.

## Tech Stack

- **Streamlit** — UI with Kanban board and RAG chat
- **OpenAI Whisper** — Local audio transcription
- **LangChain** — LLM orchestration, prompt management, output parsing
- **Ollama (phi3:latest)** — Local LLM for task extraction and RAG responses
- **Ollama (nomic-embed-text:latest)** — Embedding model for vector search
- **ChromaDB** — Vector store for memo storage and retrieval

## Project Structure

```
voice2tasks/
├── app.py              # Streamlit UI (upload, kanban, export, RAG chat)
├── transcriber.py      # Whisper local transcription
├── task_extractor.py   # LangChain + Ollama → structured task extraction
├── rag_engine.py       # ChromaDB + LangChain retrieval for querying memos
├── requirements.txt    # Python dependencies
├── chroma_db/          # ChromaDB persistent storage (auto-created)
└── README.md
```

## Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/voice2tasks.git
cd voice2tasks

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Ensure Ollama is running and accessible at the configured base URL:

```
	http://localhost:11434
```

2. Pull the required models:

```bash
ollama pull phi3:latest
ollama pull nomic-embed-text:latest
```

3. To change the Ollama base URL, update `base_url` in:
   - `task_extractor.py`
   - `rag_engine.py`

## Usage

```bash
streamlit run app.py
```

1. **Upload** a voice memo (.wav, .mp3, .m4a, .ogg) via the sidebar
2. **View** extracted tasks on the Kanban board (Todo / In Progress / Done)
3. **Move** tasks between columns using the status dropdown
4. **Ask** questions about your memos using the RAG chat in the sidebar
5. **Download** your tasks as a .txt file

## Notes

- Whisper uses the `base` model by default. For better accuracy, change to `small` or `medium` in `transcriber.py` (requires more RAM)
- ChromaDB data persists in the `chroma_db/` directory — delete it to reset
- The task extractor uses a JSON output parser to enforce structured output from the LLM
- Streamlit session state holds tasks in-memory — they reset on app restart (use the download button to save)

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [MIT License](LICENSE) file for details.
