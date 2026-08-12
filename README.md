<div align="center">

# Awesome AI Agents

**Open-source AI agents you can clone and run locally — privacy-first apps for writing, learning, productivity, and more.**

Clone it · Run it · Learn from it · Ship your own  
Works with local models via [Ollama](https://ollama.com/) — Llama, Qwen, Gemma, Phi, and friends.

**[Run one now](#-run-one-now)** · **[Browse agents](#-browse-agents)** · **[What you'll learn](#-what-youll-learn)** · **[Contributing](#-contributing)**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Local_LLM-Ollama-black)](https://ollama.com/)

</div>

---

## 🌟 Why This Repo?

Most “AI agent” tutorials stop at a notebook. This repo is the opposite: a growing collection of **real, runnable agents** — each in its own folder, with a UI, clear structure, and a README you can follow end to end.

Here you’ll find:

- **20+ hand-built agents** across writing, study, productivity, media, data, and personal use
- **Local-first by default** — your data stays on your machine; most projects need no paid LLM API
- **Patterns you can reuse** — prompt chains, RAG, tool-calling agents, multi-agent crews, voice pipelines
- **Beginner-friendly starting points**, plus room to grow into tools, memory, and MCP

Whether you’re learning LangChain, exploring Ollama, or prototyping your next side project — pick a folder and start building.

> New agents are added continuously. Star the repo to follow along.

---

## 🚀 Run One Now

Get from zero to a working agent in under a minute:

```bash
git clone https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents/ai-email-generator
pip install -r requirements.txt
streamlit run app.py
```

Make sure [Ollama](https://ollama.com/) is running and you’ve pulled a model (e.g. `ollama pull llama3.2`). Then describe the email you want — subject and body appear in the UI, and you can refine with follow-up feedback.

**Prefer a single folder only?** Use sparse checkout:

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout init --cone
git sparse-checkout set ai-email-generator
git checkout
cd ai-email-generator
pip install -r requirements.txt
streamlit run app.py
```

Every project folder has its own `README.md` with models, env vars, and exact run steps.

---

## 🗺️ Where to Start

Not sure which agent to open first? A simple path:

1. **First local chat** — [Simple AI Assistant](./simple-AI-assistant) (FastAPI + Ollama, no framework noise)
2. **First Streamlit agent** — [AI Email Generator](./ai-email-generator) or [AI Grammar Checker](./ai-grammer-checker)
3. **First RAG** — [AI PDF Chat](./ai-pdf-chat) or [AI Notes Summarizer](./ai-notes-summarizer)
4. **First multi-agent** — [AI News Generator](./ai_news_generator) (CrewAI) or [Breakup Recovery AI](./breakup-recovery-ai) (LangGraph)
5. **First tool-using agent** — [AI Data Analysis Agent](./ai-data-analysis-agent) *(intermediate — SQL + Python tools over your CSV/Excel)*

---

## 🧠 What You'll Learn

These aren’t toy prompts. Across the collection you’ll see production-adjacent building blocks:

| Pattern | Where it shows up |
|---|---|
| Prompt chaining & map-reduce | Meeting minutes, cover letters, notes summarizer, webpage summarizer |
| Conversational RAG | PDF chat, voice memos, chat-with-audio |
| Tool-calling agents | Data analysis (DuckDB + Python), DataOps (MCP + approval gates) |
| Multi-agent workflows | News crew (CrewAI), recovery flow (LangGraph) |
| Voice & multimodal | Whisper transcription, YouTube summarization, hybrid audio RAG |
| Local embeddings & vector DBs | ChromaDB, Qdrant, hybrid dense + sparse search |

Stack details live in each project’s README — this repo is organized by **what the agent does**, not by framework.

---

## 📂 Browse Agents

### ✍️ Content & Writing

*Turn rough ideas into emails, posts, cover letters, articles, and docs — grounded where it matters, private by default.*

*   [✉️ AI Email Generator](./ai-email-generator) — Describe what you need; get a polished subject + body, then refine with feedback
*   [💼 AI LinkedIn Post Generator](./ai-linkedin-post-generator) — Keyword-driven LinkedIn posts researched with live web search (Exa), not just LLM guesswork
*   [🐦 AI Tweet Generator](./ai-tweet-generator) — Extract topics, search the web (Tavily), and ship a catchy tweet with hashtags
*   [📝 AI Grammar Checker](./ai-grammer-checker) — Fix grammar, spelling, and clarity while preserving your voice
*   [📄 AI Cover Letter Generator](./AI-Coverletter-Generator) — Resume PDF + job description → personalized cover letter via a map-reduce pipeline
*   [📰 AI News Generator](./ai_news_generator) — A two-agent crew researches a topic and writes a cited article end to end
*   [📘 AI README Generator](./ai-readme-generator) — Scan a local codebase, embed it, and generate a project README from the CLI

### 📚 Study & Learning

*Turn notes and documents into study material you can actually use — flashcards, quizzes, and clean summaries.*

*   [🃏 AI Flashcard Generator](./ai-flashcard-generator) — Q&A flashcards from text, PDF, or TXT — browse in the UI or download as CSV
*   [❓ AI Quiz Generator](./ai-quiz-generator) — Interactive multiple-choice quizzes from your notes, with scoring and export
*   [📌 AI Notes Summarizer](./ai-notes-summarizer) — Long notes and docs → coherent summaries using map-reduce over chunks

### ✅ Productivity

*Meeting notes, voice dumps, chats, webpages, and PDFs — agents that clear the backlog.*

*   [📋 AI Meeting Minutes Generator](./ai-meeting-minutes-generator) — Raw transcript → structured Minutes of Meeting through a 10-step prompt chain
*   [🎤 Voice2Tasks](./voice2tasks) — Voice memos → structured tasks, a Kanban board, and RAG chat over past memos
*   [💬 Simple AI Assistant](./simple-AI-assistant) — Local ChatGPT-style chat: FastAPI backend + a single HTML frontend
*   [🌐 AI Webpage Summarizer](./ai-webpage-summarizer) — Paste a URL → cleaned scrape → paragraph summary plus key bullets
*   [📚 AI PDF Chat](./ai-pdf-chat) — Upload PDFs, index them, and ask questions in a conversational RAG chat

### 🎧 Media & Audio

*Listen, transcribe, summarize, and talk to recordings — fully local pipelines.*

*   [🎧 Chat with Audio](./chat-with-audio) — Transcribe with Whisper, hybrid-search the transcript, and RAG-chat your recordings
*   [▶️ YouTube Video Summarizer](./YouTube-Video-Summarization-Application) — YouTube URL → download audio → Whisper transcript → concise local summary

### 📊 Data & Ops

*Ask questions of spreadsheets and databases in plain English — with guardrails when writes get risky.*

*   [📈 AI Data Analysis Agent](./ai-data-analysis-agent) — Upload CSV/Excel and ask natural-language questions *(intermediate — SQL + Python tools via DuckDB)*
*   [🗄️ DataOps Agent](./DataOps-Agent) — Natural-language database ops over MCP, with session memory and human approval for writes

### 💚 Personal

*Agents for reflection and support — multi-step flows, not a single chatbot reply.*

*   [💚 Breakup Recovery AI](./breakup-recovery-ai) — A LangGraph sequence: therapist → closure → routine → honest feedback (with optional web grounding)

---

## 🛠️ How Projects Are Structured

Most agents follow a familiar layout so you can jump between folders without relearning the map:

```text
some-agent/
├── app.py              # UI (often Streamlit or Gradio)
├── main.py             # Core logic — chains, agents, RAG
├── requirements.txt
├── README.md           # Models, setup, run steps
└── .env.example        # When API keys or URLs are needed
```

**Common prerequisites**

- Python 3.10+
- [Ollama](https://ollama.com/) running locally (or a remote Ollama URL)
- The model named in that project’s README (`ollama pull …`)

A few projects add Docker (e.g. Qdrant) or a small web-search API key (Exa / Tavily) — called out clearly in their READMEs.

---

## 🤝 Contributing

New agents, fixes, and doc improvements are welcome.

1. Fork the repo and create a branch
2. Add or update an agent in its **own folder** (`README.md`, `requirements.txt`, clear run steps)
3. List new agents under the right [category](#-browse-agents) in this README
4. Open a PR describing what changed and how to run it

Keep agents self-contained, local-first when possible, and never commit secrets (use `.env.example`). Ideas or questions? [Open an issue](https://github.com/IshaanLabs/Awesome-AI-Agents/issues).

---

## 📜 License

Licensed under the [Apache License 2.0](LICENSE) — free to use, modify, and share.

---

## 💬 Connect

Questions, ideas, or collaboration — [open an issue](https://github.com/IshaanLabs/Awesome-AI-Agents/issues).

⭐ Star the repo to get notified when new agents drop.

**Happy building!**
