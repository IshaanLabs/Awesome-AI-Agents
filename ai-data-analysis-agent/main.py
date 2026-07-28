import json
from tools import preprocess_and_save, setup_duckdb, get_tools

SYSTEM_PROMPT_TEMPLATE = """You are an expert data analyst. You have access to a DuckDB SQL database with a table called `uploaded_data`.

The table schema is:
{schema}

To answer the user's question, call the appropriate tool by responding ONLY with a JSON object in this exact format:
{{"name": "<tool_name>", "arguments": {{<args>}}}}

Available tools:
- sql_db_query: Run a SQL query. Arguments: {{"query": "<SQL>"}}
- sql_db_query_checker: Check a SQL query before running. Arguments: {{"query": "<SQL>"}}

Rules:
- ONLY use column names that exist in the schema above. Never guess column names.
- Always query the `uploaded_data` table.
- If a query fails, re-read the schema and fix the column names.
- After getting the query result, respond with a clear final answer in plain text (not JSON)."""


def run_agent(file, user_query: str):
    print("\n" + "=" * 60)
    print(f"[MAIN] Starting agent pipeline")
    print(f"[MAIN] Query: {user_query}")
    print("=" * 60)

    # Step 1: Preprocess file
    temp_csv_path, columns, df = preprocess_and_save(file)
    if temp_csv_path is None:
        print("[MAIN] ERROR: File preprocessing failed")
        return None

    # Step 2: Load into DuckDB
    db_uri = setup_duckdb(temp_csv_path)
    if db_uri is None:
        print("[MAIN] ERROR: DuckDB setup failed")
        return None

    # Step 3: Get tools and LLM
    tools, llm = get_tools(db_uri, df)

    # Step 4: Build tool map for manual execution
    tool_map = {t.name: t for t in tools}
    print(f"[MAIN] Tool map: {list(tool_map.keys())}")

    # Step 5: Fetch schema upfront and inject into system prompt
    print("[MAIN] Fetching table schema")
    schema = tool_map["sql_db_schema"].invoke("uploaded_data")
    print(f"[MAIN] Schema: {schema[:300]}")
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(schema=schema)

    # Step 6: Run agentic loop manually (model outputs JSON tool calls as text)
    print(f"[MAIN] Running query: {user_query}")
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query),
    ]

    try:
        for iteration in range(8):
            print(f"[MAIN] Iteration {iteration + 1}")
            response = llm.invoke(messages)
            content  = response.content.strip()
            print(f"[MAIN] LLM output: {content[:200]}")

            import re

            # Strip markdown code fences if present
            clean = content
            if "```" in clean:
                match = re.search(r"```(?:json)?\s*({.*?})\s*```", clean, re.DOTALL)
                clean = match.group(1) if match else clean
            else:
                match = re.search(r'(\{\s*"name"\s*:.*?\})', clean, re.DOTALL)
                if match:
                    # Check if there's substantial plain text alongside the JSON (model answered early)
                    non_json = clean.replace(match.group(1), "").strip()
                    # Clean up any leftover JSON punctuation
                    non_json = re.sub(r'^[\}\]\s,]+', '', non_json).strip()
                    if len(non_json) > 40 and not non_json.startswith("{"):
                        print(f"[MAIN] Model mixed tool call + answer, extracting answer part")
                        print(f"[MAIN] Final answer received")
                        return non_json
                    clean = match.group(1)

            # Try to parse as a tool call JSON
            try:
                parsed = json.loads(clean)
                tool_name = parsed.get("name")
                tool_args = parsed.get("arguments", {})

                if tool_name and tool_name in tool_map:
                    print(f"[MAIN] Calling tool: {tool_name} | args: {tool_args}")
                    # Invoke tool — most LangChain tools accept a single string or dict
                    tool_input = tool_args.get("query") or tool_args.get("table_names") or tool_args.get("tool_input", "")
                    observation = tool_map[tool_name].invoke(tool_input)
                    print(f"[MAIN] Tool result: {str(observation)[:300]}")

                    messages.append(AIMessage(content=content))
                    # If tool returned an error, explicitly tell the model to fix using the schema
                    if "Error" in str(observation) or "error" in str(observation):
                        messages.append(HumanMessage(content=(
                            f"Tool result (ERROR): {observation}\n\n"
                            f"The query failed. Check the schema again:\n{schema}\n"
                            "Fix the column names and try again with the correct columns."
                        )))
                    else:
                        messages.append(HumanMessage(content=f"Tool result: {observation}\n\nNow provide the final answer to the user in plain text."))
                    continue

            except (json.JSONDecodeError, TypeError):
                pass

            # Not a tool call — this is the final answer
            print(f"[MAIN] Final answer received")
            return content

        print("[MAIN] Max iterations reached")
        return messages[-1].content if messages else "No answer returned"

    except Exception as e:
        print(f"[MAIN] ERROR during agent execution: {e}")
        return f"Error: {e}"


if __name__ == "__main__":
    import sys

    print("[MAIN] Running in terminal test mode")

    # Quick terminal test — pass a real CSV file path and query
    test_file_path = "test.csv"
    test_query     = "How many rows are in the dataset?"

    try:
        with open(test_file_path, "rb") as f:
            # Wrap in a simple object to mimic Streamlit's UploadedFile
            class FakeFile:
                def __init__(self, f, name):
                    self.name = name
                    self._f   = f
                def read(self, *args):   return self._f.read(*args)
                def seek(self, *args):   return self._f.seek(*args)
                def readline(self, *a):  return self._f.readline(*a)
                def __iter__(self):      return iter(self._f)

            fake_file = FakeFile(f, test_file_path)
            answer    = run_agent(fake_file, test_query)
            print(f"\n[RESULT] {answer}")

    except FileNotFoundError:
        print(f"[MAIN] No test file found at '{test_file_path}'. Place a CSV there to test.")
        sys.exit(1)
