# 🤖 ai-newsroom

> An AI-powered news article generator that autonomously researches any topic on the web and produces a fully written, cited blog post — powered by CrewAI agents, Ollama (Qwen3), and DuckDuckGo Search.

---

## 📌 About

**ai-newsroom** uses a two-agent CrewAI pipeline to turn any topic into a publication-ready markdown article:

1. **Senior Research Analyst** — searches the web using DuckDuckGo, gathers real-time data, facts, and source URLs
2. **Content Writer** — transforms the research brief into an engaging, well-structured blog post with inline citations

The entire workflow runs locally via Ollama, with no dependency on paid LLM APIs. The UI is built with Gradio for a clean, full-screen experience.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | [CrewAI](https://github.com/crewAIInc/crewAI) |
| LLM | [Qwen3 4B (q4_K_M)](https://ollama.com/library/qwen3) via [Ollama](https://ollama.com) |
| Web Search | [DuckDuckGo Search (ddgs)](https://github.com/deedy5/ddgs) |
| UI | [Gradio](https://gradio.app) |
| Config | [python-dotenv](https://github.com/theskumar/python-dotenv) |

---

## 📁 Project Structure

```
ai-newsroom/
├── main.py            # All agents, tasks, crew logic and Gradio UI
├── .env               # Environment variables (Ollama base URL)
├── requirements.txt   # Python dependencies
└── README.md
```

---

## ⚙️ Installation

**1. Clone the repository**
```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set ai_news_generator
git checkout
cd ai_news_generator
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Pull the model on your Ollama server**
```bash
ollama pull qwen3:4b-q4_K_M
```

---

## 🔧 Configuration

Create a `.env` file in the project root:

```env
OLLAMA_BASE_URL=http://<your-ollama-server-ip>:11434
```

- If running Ollama locally, use `http://localhost:11434`
- If running on a remote server, replace with the server's IP or hostname

---

## 🚀 Usage

```bash
python main.py
```

Then open your browser at `http://127.0.0.1:7860`

1. Enter a topic in the input box (e.g. `Kimi K3 newly launched model`)
2. Adjust the temperature slider if needed — higher values produce more creative output
3. Click **Generate Article**
4. Wait for the agents to research and write the article
5. Download the result as a `.md` file

---

## 📝 Notes

- **Model choice matters** — Qwen3 4B supports native tool calling, which is required for the research agent to correctly use DuckDuckGo. 
- **Search failures** — if DuckDuckGo returns no results, the pipeline stops early and reports the failure instead of generating fabricated content.
- **Remote Ollama** — make sure port `11434` is open and accessible from your machine if using a remote server.
- Generated `.md` files are saved in the project root directory.

---

## 🤝 Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the MIT License — see the [MIT License](https://opensource.org/licenses/MIT) file for details.
