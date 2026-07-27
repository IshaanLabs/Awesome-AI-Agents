# 💔 Breakup Recovery Squad

### *Because your friends are tired of hearing about it.* 😂

### *The only therapist that won't ghost you.*

An AI-powered breakup recovery assistant that gives you empathetic support, closure exercises, a 7-day recovery plan, and brutally honest feedback — all from a single story you share.

Built with LangGraph for multi-agent orchestration, LangChain + Ollama for local LLM inference, and Streamlit for the UI.

---

## Tech Stack

| Layer               | Technology                                                |
| ------------------- | --------------------------------------------------------- |
| LLM                 | Ollama —`qwen2.5vl:7b` (vision-language)               |
| Agent Orchestration | LangGraph                                                 |
| LLM Framework       | LangChain (`langchain-ollama`, `langchain-community`) |
| Web Search          | DuckDuckGo (`duckduckgo-search`)                        |
| UI                  | Streamlit                                                 |
| Language            | Python 3.11+                                              |

---

## Project Structure

```
breakup-recovery-ai/
├── agents.py          # 4 agent functions (therapist, closure, routine, honesty)
├── main.py            # LangGraph state graph wiring all agents sequentially
├── app.py             # Streamlit UI
├── requirements.txt   # Python dependencies
└── README.md
```

### File Responsibilities

- `agents.py` — each agent is a plain function that takes user text + image paths, builds a prompt, calls the LLM, and returns a markdown string. The brutal honesty agent also runs a DuckDuckGo search to ground its response.
- `main.py` — defines `RecoveryState` (TypedDict), wraps each agent as a LangGraph node, and wires them in sequence: `therapist → closure → routine → honesty`. Exposes `run_graph()` and `build_graph()`.
- `app.py` — Streamlit frontend with a dark warm theme, image upload, live progress bar via `graph.stream()`, and results rendered in 4 color-coded tabs.

---

## Installation

**1. Clone the repository**

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set breakup-recovery-ai
git checkout
cd breakup-recovery-ai
```

**2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**3. Install Ollama and pull the model**

Download Ollama from [ollama.com](https://ollama.com) then run:

```bash
ollama pull qwen2.5vl:7b
```

---

## Configuration

Open `agents.py` and update the two constants at the top of the file:

```python
OLLAMA_BASE_URL = "http://localhost:11434"   # your Ollama server URL
MODEL_NAME      = "qwen2.5vl:7b"            # model tag
```

That's the only configuration needed — no API keys, no `.env` file.

---

## Usage

**Start Ollama**

```bash
ollama serve
```

**Run the Streamlit app**

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

**In the UI:**

1. Type your story in the left panel — describe what happened and how you're feeling
2. Optionally upload chat screenshots (jpg/png) — the vision model will read them
3. Click **Get My Recovery Plan 💝**
4. Watch the progress bar as each agent completes
5. Read your results across 4 tabs:
   - 🤗 Emotional Support
   - ✍️ Find Closure
   - 📅 Recovery Plan
   - 💪 Honest Perspective

**Run via CLI (no UI)**

```bash
python main.py
```

---

## Notes

- All inference runs locally via Ollama — no data leaves your machine
- `qwen2.5vl:7b` is a vision-language model, so uploaded images are genuinely analyzed alongside your text
- The 4 agents run sequentially — expect ~2–4 minutes total on a mid-range machine
- Print-based logs with `[agents]`, `[main]`, and `[app]` prefixes appear in your terminal for easy tracing
- Uploaded images are saved temporarily to the system temp directory and are not persisted

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License — see the [MIT License](https://opensource.org/licenses/MIT) file for details.
