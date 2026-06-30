# ✍️ AI LinkedIn Post Generator

## AI LinkedIn Post Generator | Ollama + Exa Search | Open Source | Local LLM

An open-source, locally-running LinkedIn post generator powered by **Ollama (gemma3)** and **Exa Search**. Enter your keywords, describe what you want to say, and get a polished, ready-to-post LinkedIn post — grounded in real web research, zero hallucination.

> No OpenAI. No cloud LLM costs. Runs entirely on your machine.

---

## Tech Stack

| Layer | Tool |
|---|---|
| UI | [Streamlit](https://streamlit.io/) |
| LLM | [Ollama](https://ollama.com/) — `gemma3:latest` (local) |
| Web Search | [Exa](https://exa.ai/) — neural search API |
| Language | Python 3.10+ |

---

## Project Structure

```
linkedin-post-creator/
│
├── app.py              # Streamlit UI — two-column layout, inputs and output
├── main.py             # Core logic — Exa search, prompt building, Ollama generation
├── .env                # API keys and Ollama URL (not committed to git)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## Installation

**1. Clone the repository**
```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set ai-linkedin-post-generator
git checkout
cd linkedin-post-creator
```

**2. Install Python dependencies**
```bash
pip install -r requirements.txt
```

**3. Install and set up Ollama**

Download Ollama from [ollama.com](https://ollama.com/download), then pull the gemma3 model:
```bash
ollama pull gemma3
ollama serve
```

---

## Configuration

Create a `.env` file in the project root (or rename the existing `.env`):

```env
EXA_API_KEY=your_exa_api_key_here
OLLAMA_URL=http://localhost:11434
```

- Get your free Exa API key at [dashboard.exa.ai](https://dashboard.exa.ai)
- `OLLAMA_URL` defaults to `http://localhost:11434` — change this if you're running Ollama on a remote server

---

## Usage

**1. Make sure Ollama is running**
```bash
ollama serve
```

**2. Run the app**
```bash
streamlit run app.py
```

**3. Open your browser** at `http://localhost:8501`

**4. Fill in the inputs:**
- **Keywords** — topic keywords for your post
- **Description** *(optional but recommended)* — describe what angle or message you want the post to convey
- **Post Type** — General, How-to Guide, Listicle, Poll, FAQs, Checklist, etc.
- **Length** — Short, Medium, or Long
- **Language** — English, Hindi, Spanish, Vietnamese, Chinese

**5. Click Generate** — the app searches the web via Exa, builds a grounded prompt, and generates your post via Ollama locally.

---

## Notes

- The app will **refuse to generate a post if Exa search fails** — this is intentional to prevent hallucinated content. Always ensure your `EXA_API_KEY` is valid.
- All generation happens **locally via Ollama** — your content never leaves your machine (only the search query goes to Exa).
- Terminal logs are printed at every step (`[SEARCH]`, `[FORMAT]`, `[PROMPT]`, `[LLM]`) so you can follow exactly what's happening.
- The Exa free tier allows a limited number of searches per month — check your usage at [dashboard.exa.ai](https://dashboard.exa.ai).

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) file for details.
