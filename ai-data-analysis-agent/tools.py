import tempfile
import csv
import duckdb
import pandas as pd
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_experimental.tools import PythonAstREPLTool
from langchain_ollama import ChatOllama

# ── Config ────────────────────────────────────────────────────────────────────

MODEL    = "qwen2.5-coder:7b-instruct-q5_K_M"
BASE_URL = "http://localhost:11434"

# ── LLM ───────────────────────────────────────────────────────────────────────
def get_llm():
    print(f"[LLM] Initializing ChatOllama | model={MODEL} | base_url={BASE_URL}")
    llm = ChatOllama(model=MODEL, base_url=BASE_URL, temperature=0)
    print("[LLM] ChatOllama initialized successfully")
    return llm


# ── Preprocessing ─────────────────────────────────────────────────────────────
def preprocess_and_save(file):
    print(f"[PREPROCESS] Reading file: {file.name}")
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file, encoding="utf-8", na_values=["NA", "N/A", "missing"])
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file, na_values=["NA", "N/A", "missing"])
        else:
            print("[PREPROCESS] ERROR: Unsupported file format")
            return None, None, None

        print(f"[PREPROCESS] Loaded DataFrame | rows={len(df)} | cols={list(df.columns)}")

        # Quote string columns
        for col in df.select_dtypes(include=["object"]):
            df[col] = df[col].astype(str).replace({r'"': '""'}, regex=True)

        # Parse dates and numerics
        for col in df.columns:
            if "date" in col.lower():
                df[col] = pd.to_datetime(df[col], errors="coerce")
                print(f"[PREPROCESS] Parsed date column: {col}")
            elif df[col].dtype == "object":
                try:
                    df[col] = pd.to_numeric(df[col])
                    print(f"[PREPROCESS] Converted to numeric: {col}")
                except (ValueError, TypeError):
                    pass

        # Save to temp CSV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            temp_csv_path = tmp.name
        df.to_csv(temp_csv_path, index=False, quoting=csv.QUOTE_ALL)
        print(f"[PREPROCESS] Saved temp CSV: {temp_csv_path}")

        return temp_csv_path, df.columns.tolist(), df

    except Exception as e:
        print(f"[PREPROCESS] ERROR: {e}")
        return None, None, None


# ── DuckDB Setup ──────────────────────────────────────────────────────────────
def setup_duckdb(temp_csv_path: str):
    print(f"[DUCKDB] Loading CSV into DuckDB | path={temp_csv_path}")
    try:
        # Generate a unique path without pre-creating the file (DuckDB needs a clean path)
        import uuid
        db_path = tempfile.gettempdir() + f"/duckdb_{uuid.uuid4().hex}.db"

        conn = duckdb.connect(db_path)
        conn.execute(f"""
            CREATE OR REPLACE TABLE uploaded_data AS
            SELECT * FROM read_csv_auto('{temp_csv_path}', header=true)
        """)
        row_count = conn.execute("SELECT COUNT(*) FROM uploaded_data").fetchone()[0]
        print(f"[DUCKDB] Table 'uploaded_data' created | rows={row_count}")
        conn.close()

        db_uri = f"duckdb:///{db_path}"
        print(f"[DUCKDB] Database URI: {db_uri}")
        return db_uri

    except Exception as e:
        print(f"[DUCKDB] ERROR: {e}")
        return None


# ── LangChain Tools ───────────────────────────────────────────────────────────
def get_tools(db_uri: str, df: pd.DataFrame):
    print("[TOOLS] Setting up LangChain tools")

    # SQL tools via SQLDatabaseToolkit
    print(f"[TOOLS] Connecting SQLDatabase | uri={db_uri}")
    db     = SQLDatabase.from_uri(db_uri)
    llm    = get_llm()
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    sql_tools = toolkit.get_tools()
    print(f"[TOOLS] SQL tools loaded: {[t.name for t in sql_tools]}")

    # Pandas REPL tool
    pandas_tool = PythonAstREPLTool(locals={"df": df})
    pandas_tool.name        = "pandas_repl"
    pandas_tool.description = (
        "Use this to run Python/pandas code on the DataFrame `df`. "
        "Useful for data manipulation, plotting, or operations not suited for SQL."
    )
    print("[TOOLS] PythonAstREPLTool (pandas) loaded")

    all_tools = sql_tools + [pandas_tool]
    print(f"[TOOLS] Total tools available: {len(all_tools)}")
    return all_tools, llm
