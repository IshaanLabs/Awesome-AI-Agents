# Simple AI Assistant

A local ChatGPT-style conversational AI assistant powered by [Ollama](https://ollama.com). This is a beginner-friendly starting point for anyone looking to understand how to build AI-powered applications from scratch, running entirely on your own machine with no API keys or cloud costs.

---

## Tech Stack

| Layer               | Technology                                            |
| ------------------- | ----------------------------------------------------- |
| Backend             | [FastAPI](https://fastapi.tiangolo.com/)                 |
| AI Runtime          | [Ollama](https://ollama.com)                             |
| Ollama Client       | [ollama-python](https://github.com/ollama/ollama-python) |
| Frontend            | Vanilla HTML + CSS + JavaScript                       |
| Markdown Rendering  | [marked.js](https://marked.js.org/)                      |
| Syntax Highlighting | [highlight.js](https://highlightjs.org/)                 |

---

## Project Structure

```
Simple_AI_assistant/
├── main.py           # FastAPI backend — chat, models, and static file endpoints
├── index.html        # Frontend — full chat UI (single file, no build tools)
├── requirements.txt  # Python dependencies
└── README.md
```

---

## Installation

**Prerequisites**

- Python 3.9+
- [Ollama](https://ollama.com) installed and running locally

**1. Clone the repo**

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set simple-AI-assistant
git checkout
cd simple-AI-assistant
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Pull a model via Ollama**

```bash
ollama pull llama3.2
```

> You can use any model available on [Ollama&#39;s model library](https://ollama.com/library) — e.g. `mistral`, `gemma3`, `phi4`, `deepseek-r1`.

---

## Configuration

No environment variables or config files are required. The only setting to be aware of is the default model in `main.py`:

```python
DEFAULT_MODEL = "llama3.2"
```

Change this to any model you have pulled locally. The UI also lets you switch models at runtime from the sidebar.

---

## Usage

**Start the server**

```bash
uvicorn main:app --reload
```

**Open in your browser**

```
http://localhost:8000
```

**Features available in the UI**

- **Model selector** — switch between any locally installed Ollama model from the sidebar
- **System prompt** — customize the assistant's persona from the sidebar; takes effect on the next message
- **Streaming responses** — replies stream token by token with live markdown rendering
- **Code blocks** — syntax highlighted with a one-click copy button
- **New chat** — clears the conversation and returns to the welcome screen
- **Regenerate** — re-runs the last user message
- **Copy message** — copies any AI response to clipboard

---

## Notes

- All inference runs **locally** on your machine — no data is sent to any external service
- The conversation history is kept **in-memory** in the browser; refreshing the page starts a new session
- Changing the system prompt mid-conversation takes effect on the next message sent
- Response quality and speed depend on the model you choose and your hardware (GPU recommended for larger models)

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License — see the [MIT License](https://opensource.org/licenses/MIT) file for details.
