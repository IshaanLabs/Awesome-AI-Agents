# 📝 AI Cover Letter Generator

An intelligent cover letter generator that takes your resume (PDF) and a job description as input, and produces a professional, personalized cover letter using a local LLM via Ollama. Built with a Map-Reduce LangChain pipeline to keep context lean and output focused.

---

## Tech Stack

| Layer                 | Technology                     |
| --------------------- | ------------------------------ |
| UI                    | Streamlit                      |
| LLM Inference         | Ollama (remote URL)            |
| LLM Wrappers & Chains | LangChain (LCEL)               |
| PDF Parsing           | Unstructured (via LangChain)   |
| Text Splitting        | RecursiveCharacterTextSplitter |
| Config Management     | python-dotenv                  |

---

## Project Structure

```
AI-Coverletter-Generator/
├── app.py              # Streamlit UI
├── main.py             # Core logic — PDF loading, chains, cover letter generation
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not committed)
└── README.md
```

---

## Installation

1. Clone the repository:

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set AI-Coverletter-Generator
git checkout
cd AI-Coverletter-Generator
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

4. Install system dependencies for PDF parsing:

```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils tesseract-ocr

# macOS
brew install poppler tesseract
```

---

## Configuration

Create a `.env` file in the project root:

```env
OLLAMA_BASE_URL=http://localhost:11434
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

| Variable            | Description                          | Default                |
| ------------------- | ------------------------------------ | ---------------------- |
| `OLLAMA_BASE_URL` | Remote Ollama server URL             | http://localhost:11434 |
| `CHUNK_SIZE`      | Resume chunk size in characters      | `1000`               |
| `CHUNK_OVERLAP`   | Overlap between chunks in characters | `200`                |

---

## Usage

1. Make sure your Ollama remote server is running and accessible.
2. Start the app:

```bash
streamlit run app.py
```

3. In the UI:
   - Select an Ollama model from the dropdown (fetched dynamically from your remote URL)
   - Upload your resume as a PDF
   - Paste the job description
   - Click **Generate Cover Letter**
   - Download the result as a `.txt` file

---

## Notes

- The generation follows a **3-step Map-Reduce pipeline**:
  1. **Map** — each resume chunk is checked for relevance against the job description
  2. **Reduce** — relevant chunks are condensed into a clean candidate summary
  3. **Generate** — the cover letter is produced from the condensed summary
- This approach avoids bloating the context window and keeps the output focused and relevant
- Progress is logged to the terminal at each step for easy debugging
- Ensure your Ollama instance has at least one model pulled before running the app

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) file for details.
