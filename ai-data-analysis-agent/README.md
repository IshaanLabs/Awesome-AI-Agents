# 📊 Data Analyst Agent

A local, privacy-first data analyst agent that lets you upload any CSV or Excel file and ask natural language questions about your data — powered entirely by an open-source LLM running on your machine via Ollama. No API keys. No data leaves your system.

---

## Tech Stack

| Layer           | Technology                                                                                          |
| --------------- | --------------------------------------------------------------------------------------------------- |
| LLM             | [Ollama](https://ollama.com) — `qwen2.5-coder:7b-instruct-q5_K_M` (local)                          |
| LLM Framework   | [LangChain](https://www.langchain.com) + [LangChain Community](https://github.com/langchain-ai/langchain) |
| SQL Engine      | [DuckDB](https://duckdb.org) via `duckdb-engine` + SQLAlchemy                                        |
| Data Tools      | `SQLDatabaseToolkit` (LangChain), `PythonAstREPLTool` (LangChain Experimental)                  |
| Data Processing | [Pandas](https://pandas.pydata.org)                                                                    |
| UI              | [Streamlit](https://streamlit.io)                                                                      |
| Language        | Python 3.10+                                                                                        |

---

## Project Structure

```
newagent/
├── tools.py          # Model config, preprocessing, DuckDB setup, LangChain tools
├── main.py           # Agent pipeline (run_agent), terminal testable
├── app.py            # Streamlit UI
├── test.csv          # Sample sales dataset for testing
├── requirements.txt  # Python dependencies
└── README.md
```

**How the files connect:**

```
tools.py  ──→  main.py (run_agent)  ──→  app.py (Streamlit UI)
```

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/IshaanLabs
cd ai-data-analysis-agent
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

**4. Install Ollama**

Download and install Ollama from [https://ollama.com/download](https://ollama.com/download), then pull the model:

```bash
ollama pull qwen2.5-coder:7b-instruct-q5_K_M
```

---

## Configuration

All model configuration lives at the top of `tools.py`:

```python
MODEL    = "qwen2.5-coder:7b-instruct-q5_K_M"
BASE_URL = "http://localhost:11434"
```

| Variable     | Description       | Default                              |
| ------------ | ----------------- | ------------------------------------ |
| `MODEL`    | Ollama model name | `qwen2.5-coder:7b-instruct-q5_K_M` |
| `BASE_URL` | Ollama server URL | `http://localhost:11434`           |

To switch models, update `MODEL` to any Ollama-supported model with tool-calling capability (e.g. `llama3.1`, `qwen2.5:14b`).

---

## Usage

### Terminal (test mode)

Place a CSV file named `test.csv` in the project root, then run:

```bash
python main.py
```

This runs a hardcoded test query (`"How many rows are in the dataset?"`) against `test.csv` and prints the full agent trace to the terminal.

To change the test query, edit these lines at the bottom of `main.py`:

```python
test_file_path = "test.csv"
test_query     = "Which customer spent the most?"
```

### Streamlit UI

Make sure Ollama is running, then launch the app:

```bash
streamlit run app.py
```

1. Upload a CSV or Excel file using the sidebar
2. The app displays a data preview with row/column stats
3. Type a natural language question in the query box
4. Click **▶ Run Query** — the agent will query your data and return an answer
5. Check the terminal for the full step-by-step agent trace

**Example queries to try with `test.csv`:**

```
Which product has the highest revenue?
How many orders were cancelled?
What is the monthly sales trend?
Which customer spent the most?
What is the average discount by category?
```

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License — see the [MIT License](https://opensource.org/licenses/MIT) file for details.
