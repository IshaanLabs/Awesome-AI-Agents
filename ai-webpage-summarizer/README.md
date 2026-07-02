# 🌐 AI Website Summariser

> An AI-powered web application that scrapes any webpage, cleans the content, and generates a concise summary with key bullet points — all running 100% locally on your machine.

---

## Description

Website Summariser takes a URL as input, scrapes the page using BeautifulSoup, strips away noise (scripts, styles, navbars, footers), and feeds the cleaned text through a **map-reduce summarisation pipeline** powered by **Llama 3.2 via Ollama**.

Large pages are split into overlapping chunks at natural line/paragraph boundaries, each chunk is summarised independently, and then all chunk summaries are combined into a final coherent output — a paragraph summary plus key bullet points.

---

## Tech Stack

| Layer    | Technology                |
| -------- | ------------------------- |
| UI       | Streamlit                 |
| Scraping | Requests + BeautifulSoup4 |
| LLM      | Llama 3.2 (via Ollama)    |
| Language | Python 3.10+              |

---

## Project Structure

```
summarise_website/
│
├── app.py              # Streamlit UI — wide-screen professional interface
├── main.py             # Core logic — scraping, cleaning, chunking, summarising
└── requirements.txt    # Python dependencies
```

### Key functions in `main.py`

| Function             | Description                                                               |
| -------------------- | ------------------------------------------------------------------------- |
| `scrape(url)`      | Fetches raw HTML from the given URL                                       |
| `clean(html)`      | Strips tags, scripts, navbars, footers and returns plain text             |
| `chunk_text(text)` | Splits text into ~5000 char chunks at line boundaries with 3-line overlap |
| `call_llm(prompt)` | Sends a prompt to Llama 3.2 via Ollama and returns the response           |
| `summarise(text)`  | Runs map-reduce — summarises each chunk then combines into final output  |
| `run(url)`         | End-to-end pipeline: scrape → clean → summarise                         |

---

## Installation

**1. Clone the repository**

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set ai-webpage-summarizer
git checkout
cd ai-webpage-summarizer
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Install and start Ollama**

Download Ollama from [https://ollama.com](https://ollama.com), then:

```bash
ollama pull llama3.2
ollama serve
```

---

## Configuration

The following constants in `main.py` can be adjusted:

| Constant          | Default      | Description                                                        |
| ----------------- | ------------ | ------------------------------------------------------------------ |
| `MODEL`         | `llama3.2` | Ollama model to use for summarisation                              |
| `CHUNK_SIZE`    | `5000`     | Max characters per chunk before splitting                          |
| `OVERLAP_LINES` | `3`        | Number of lines carried over between chunks for context continuity |

To switch models, update `MODEL` in `main.py`:

```python
MODEL = "llama3.1"   # or mistral, gemma2, etc.
```

---

## Usage

**Start the Streamlit app:**

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

1. Paste any URL into the input bar
2. Click **✨ Summarise**
3. View the AI-generated summary with stats (word count, character count, bullet points)
4. Download the summary as a `.txt` file or copy it directly

---

## Notes

- Ollama must be running locally before starting the app (`ollama serve`)
- Pages behind login walls, CAPTCHAs, or JavaScript-only rendering may not scrape correctly
- Very large pages are automatically chunked — processing time scales with page size
- All processing happens locally — no data is sent to any external API

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License — see the [MIT License](https://opensource.org/licenses/MIT) file for details.
