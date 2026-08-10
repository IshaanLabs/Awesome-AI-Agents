# AI Flashcard Generator

A simple AI-powered flashcard generator that uses Ollama LLMs running locally or remotely to generate Q&A flashcards from your notes or documents. Supports plain text input as well as PDF and TXT file uploads. Flashcards are displayed interactively on a Streamlit UI and can be downloaded as a CSV file.

---

## Tech Stack

| Tool                                                                        | Purpose                             |
| --------------------------------------------------------------------------- | ----------------------------------- |
| [Streamlit](https://streamlit.io/)                                             | Frontend UI                         |
| [LangChain](https://www.langchain.com/)                                        | Prompt templates and LLM chaining   |
| [langchain-ollama](https://pypi.org/project/langchain-ollama/)                 | Ollama LLM wrapper for LangChain    |
| [langchain-core](https://pypi.org/project/langchain-core/)                     | `PromptTemplate`, `Document`    |
| [langchain-community](https://pypi.org/project/langchain-community/)           | `PyPDFLoader` and `TextLoader`  |
| [langchain-text-splitters](https://pypi.org/project/langchain-text-splitters/) | `RecursiveCharacterTextSplitter`  |
| [Ollama](https://ollama.com/)                                                  | Local/remote LLM inference          |
| [pypdf](https://pypi.org/project/pypdf/)                                       | PDF parsing backend for PyPDFLoader |

---

## Project Structure

```
ai-flashcard-generator/
├── app.py              # Streamlit UI
├── main.py             # Flashcard generation logic (LangChain + Ollama)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## Installation

1. Clone the repository:

   ```bash
   git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
   cd Awesome-AI-Agents
   git sparse-checkout set ai-flashcard-generator
   git checkout
   cd ai-flashcard-generator
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
   - Use the **slider** to set how many flashcards to generate per chunk
   - Choose an **Input Mode**:
     - **Paste Text** — directly paste your notes or content
     - **Upload File** — upload a `.pdf` or `.txt` file
   - Click **Generate Flashcards**
   - Flashcards are displayed as expandable cards — click a card to reveal the answer
   - Click **Download Flashcards as CSV** to export all cards

---

## Notes

- PDF files are loaded using LangChain's `PyPDFLoader`
- TXT files are loaded using LangChain's `TextLoader`
- Text is split into chunks of 2000 characters with 100 character overlap
- The LLM is prompted to generate flashcards in a strict `Q:` / `A:` format per chunk
- All flashcards from all chunks are collected and displayed together
- Uploaded files are saved temporarily and deleted after generation
- CSV export contains two columns: `question` and `answer`

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) file for details.
