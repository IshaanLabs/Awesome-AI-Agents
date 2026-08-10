# AI Quiz Generator

A simple AI-powered interactive quiz generator and assessment taker that uses Ollama LLMs running locally or remotely to generate multiple choice questions from your notes or documents. Supports plain text input as well as PDF and TXT file uploads. Quizzes are taken interactively on a Streamlit UI with a results screen showing your score, and can be downloaded as a TXT file.

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
ai-quiz-generator/
├── app.py              # Streamlit UI
├── main.py             # Quiz generation logic (LangChain + Ollama)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## Installation

1. Clone the repository:

   ```bash
   git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
   cd Awesome-AI-Agents
   git sparse-checkout set ai-quiz-generator
   git checkout
   cd ai-quiz-generator
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

No `.env` file or API keys are needed — everything is configured directly in the sidebar.

---

## Usage

1. Start the Streamlit app:

   ```bash
   streamlit run app.py
   ```
2. In the sidebar:

   - Enter your **Ollama Base URL** (default: `http://localhost:11434`)
   - Click **Load Models** to fetch available models from the Ollama server
   - Select a model from the dropdown (or type one manually)
   - Use the **slider** to set how many questions to generate per chunk
   - Choose an **Input Mode** — Paste Text or Upload File
3. In the main area:

   - Paste your text or upload a `.pdf` / `.txt` file
   - Click **Generate Quiz** to generate the questions
   - Answer all questions and click **Submit Quiz**
   - View your **score and results** — each question shows ✅/❌ with the correct answer highlighted
   - Click **Download Quiz as TXT** to export the quiz
   - Click **Retake Quiz** to attempt the quiz again

---

## Notes

- PDF files are loaded using LangChain's `PyPDFLoader`
- TXT files are loaded using LangChain's `TextLoader`
- Text is split into chunks of 2000 characters with 200 character overlap
- The LLM is prompted to generate questions in a strict `Q1:` / `A)` `B)` `C)` `D)` / `Answer:` format per chunk
- All questions from all chunks are collected and presented as a single quiz
- The downloaded TXT file contains all questions first, followed by all answers at the end
- Uploaded files are saved temporarily and deleted after generation

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) file for details.
