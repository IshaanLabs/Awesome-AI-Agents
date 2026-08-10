# AI Notes Summarizer

A simple AI-powered notes summarizer that uses Ollama LLMs running locally or remotely to summarize your notes using LangChain's map-reduce chain. Supports plain text input as well as PDF and TXT file uploads via a clean Streamlit UI.

---

## Tech Stack

| Tool                                                              | Purpose                                   |
| ----------------------------------------------------------------- | ----------------------------------------- |
| [Streamlit](https://streamlit.io/)                                   | Frontend UI                               |
| [LangChain](https://www.langchain.com/)                              | LLM chaining and map-reduce summarization |
| [langchain-ollama](https://pypi.org/project/langchain-ollama/)       | Ollama LLM wrapper for LangChain          |
| [langchain-classic](https://pypi.org/project/langchain-classic/)     | `load_summarize_chain` (map-reduce)     |
| [langchain-community](https://pypi.org/project/langchain-community/) | `PyPDFLoader` and `TextLoader`        |
| [Ollama](https://ollama.com/)                                        | Local/remote LLM inference                |
| [pypdf](https://pypi.org/project/pypdf/)                             | PDF parsing backend for PyPDFLoader       |

---

## Project Structure

```
ai-notes-summarizer/
├── app.py              # Streamlit UI
├── main.py             # Summarization logic (LangChain map-reduce)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## Installation

1. Clone the repository:

   ```bash
   git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
   cd Awesome-AI-Agents
   git sparse-checkout set ai-notes-summarizer
   git checkout
   cd ai-notes-summarizer
   ```
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

This app requires a running Ollama instance (local or remote).

- To run Ollama locally, install it from [https://ollama.com](https://ollama.com) and pull a model:

  ```bash
  ollama pull llama3.2
  ```
- To use a remote Ollama instance, make sure the server is accessible and note its base URL (e.g. `http://192.168.x.x:11434`).

No `.env` file or API keys are needed — everything is configured directly in the UI.

---

## Usage

1. Start the Streamlit app:

   ```bash
   streamlit run app.py
   ```
2. In the UI:

   - Enter your **Ollama Base URL** (default: `http://localhost:11434`)
   - Click **Load Models** to fetch available models from the Ollama server
   - Select a model from the dropdown (or type one manually)
   - Choose an **Input Mode**:
     - **Paste Text** — directly paste your notes
     - **Upload File** — upload a `.pdf` or `.txt` file
   - Click **Summarize** to get your summary

---

## Notes

- PDF files are loaded using LangChain's `PyPDFLoader`
- TXT files are loaded using LangChain's `TextLoader`
- Text is split into chunks of 2000 characters with 200 character overlap before summarization
- The map-reduce chain first summarizes each chunk individually (map), then combines them into a final summary (reduce)
- Uploaded files are saved temporarily and deleted after summarization

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) file for details.
