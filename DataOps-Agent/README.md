# 🤖 DataOps Agent

**An autonomous LangChain agent that connects to SafeSQL-MCP via SSE, orchestrates database operations using natural language, maintains persistent memory across sessions, and enforces human approval for risky write operations.**

```
User: "What are the top 10 products by revenue?"
→ Agent reasons → calls tools → returns formatted answer

User: "Increase all beverage prices by 5%"
→ Agent generates SQL → previews impact → asks for approval → executes

User: "What did I ask last week about orders?"
→ Agent searches memory → recalls past interactions → answers in context
```

---

## 🛠️ Tech Stack

| Component                 | Technology                                 |
| ------------------------- | ------------------------------------------ |
| **Agent Framework** | LangChain (custom ReAct loop)              |
| **LLM**             | Ollama —qwen3:4b-q4_K_M                   |
| **MCP Client**      | FastMCP 3.4+ (SSE / streamable-http)       |
| **Memory**          | Mem0 2.0+ with Qdrant vector store         |
| **Vector DB**       | Qdrant (Docker)                            |
| **Terminal UI**     | Rich                                       |
| **Backend**         | SafeSQL-MCP (LangGraph + FastMCP + SQLite) |

---

## 📁 Project Structure

```
DataOps-Agent/
│
├── agent.py            # Custom ReAct executor loop + approval interceptor
├── cli.py              # Interactive Rich terminal interface
├── config.py           # MCP URL, Ollama settings, Qdrant config
├── memory.py           # Mem0 + Qdrant — add, search, retrieve memory
├── prompts.py          # System prompt, context builder, report template
├── tools.py            # 10 LangChain tools wrapping SafeSQL-MCP via SSE
│
├── qdrant_storage/     # Qdrant Docker volume (persistent vector memory)
├── Logs/               # Agent logs (auto-created)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- [Docker](https://docs.docker.com/get-docker/) installed and running
- [Ollama](https://ollama.ai/) installed and running

### 1. Clone and set up SafeSQL-MCP (required backend)

```bash
git clone https://github.com/IshaanLabs/SafeSQL-MCP.git
cd SafeSQL-MCP
```

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
# or
venv\Scripts\activate           # Windows
```

```bash
pip install -r requirements.txt
```

### 2. Clone DataOps Agent

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set DataOps-Agent
git checkout
cd DataOps-Agent
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Pull the LLM model

```bash
ollama pull qwen3:4b-q4_K_M
```

### 5. Start Qdrant (Docker)

```bash
docker run -d --name qdrant -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

---

## ⚙️ Configuration

All settings are in `config.py`:

```python
MCP_URL          = "http://127.0.0.1:8100/mcp"   # SafeSQL-MCP server endpoint
OLLAMA_BASE_URL  = "http://localhost:11434"        # Ollama base URL
MODEL_NAME       = "qwen3:4b-q4_K_M"

QDRANT_HOST      = "localhost"
QDRANT_PORT      = 6333

AGENT_USER_ID    = "dataops_user"   # Default user for memory scoping
MAX_ITERATIONS   = 10               # Max ReAct loop iterations per query
REQUEST_TIMEOUT  = 60               # MCP tool call timeout (seconds)
```

---

## 📖 Usage

### Step 1 — Start Qdrant (if not already running)

```bash
docker start qdrant
```

### Step 2 — Start SafeSQL-MCP server

```bash
# In the SafeSQL-MCP directory
python app.py --mode http
```

Wait for: `Uvicorn running on http://0.0.0.0:8100`

### Step 3 — Run DataOps Agent

```bash
# In the DataOps-Agent directory
python cli.py
```

### CLI Commands

| Command      | Description                            |
| ------------ | -------------------------------------- |
| *any text* | Ask a natural language question        |
| `/tables`  | List all database tables               |
| `/memory`  | Show recent memory for current session |
| `/history` | Show recent audit logs                 |
| `/clear`   | Clear memory for current user          |
| `/help`    | Show available commands                |
| `/quit`    | Exit                                   |

### Example Interactions

```
You> What are the top 10 products by revenue?
You> Show me all orders from Germany in Q3 2022
You> Update beverage prices by 5%          ← triggers approval flow
You> What did I ask earlier about products? ← uses memory
```

---

## 📝 Notes

- DataOps Agent requires **SafeSQL-MCP** to be running — it is the backend that handles SQL generation, safety checks, and execution
- Memory is **persistent across sessions** via Qdrant — the agent remembers past interactions
- The **approval interceptor** in `agent.py` detects `APPROVAL REQUIRED` in tool responses and pauses to ask the user before proceeding
- The ReAct loop is **prompt-based** (not `bind_tools`) — works with any Ollama model
- Qdrant data is stored in `qdrant_storage/` — safe to back up or delete to reset memory
- Logs are written to `Logs/project_logger.log` with rotation

---

## 🤝 Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the MIT License - see the [MIT License](../LICENSE) file for details.

---

<p align="center">
  <b>DataOps Agent</b> — Talk to your database. Autonomously. 🤖
</p>
