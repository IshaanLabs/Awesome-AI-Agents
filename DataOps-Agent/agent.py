import sys
import json
import re
sys.path.insert(0, "/mnt/d/awesome/SQL_AI/DataOps-Agent")
sys.path.append("/mnt/d/awesome/SQL_AI")

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from config import OLLAMA_BASE_URL, MODEL_NAME, AGENT_USER_ID, MAX_ITERATIONS
from tools import ALL_TOOLS
from memory import add_memory, search_memory
from prompts import SYSTEM_PROMPT, build_context_prompt
from logger import get_logger

log = get_logger("agent")

_llm = None
_tools_by_name = {t.name: t for t in ALL_TOOLS}

TOOL_DESCRIPTIONS = "\n".join(
    f"- {t.name}(params: {list(t.args.keys()) or 'none'}): {t.description}"
    for t in ALL_TOOLS
)

REACT_SYSTEM = SYSTEM_PROMPT + f"""

## ReAct Format
You MUST follow this exact format for every response:

Thought: <your reasoning about what to do>
Action: <tool_name>
Action Input: <json object with tool arguments>

After receiving an Observation, continue with:
Thought: <reasoning about the observation>
Action: <next tool or "Final Answer">
Action Input: <args or the final answer text>

When you have enough information to answer, use:
Thought: I now have the answer.
Action: Final Answer
Action Input: <your complete answer to the user>

## Available Tools
{TOOL_DESCRIPTIONS}

## Rules
- ALWAYS use the ReAct format above. Never respond with plain text alone.
- Action Input MUST be valid JSON.
- Only use tool names exactly as listed above.
- For "Final Answer", Action Input is your plain text answer.
"""


def _parse_react(text: str) -> tuple[str, str, str]:
    """Returns (thought, action, action_input)."""
    thought = re.search(r"Thought:\s*(.+?)(?=\nAction:|\Z)", text, re.DOTALL)
    action = re.search(r"Action:\s*(.+?)(?=\nAction Input:|\Z)", text, re.DOTALL)
    action_input = re.search(r"Action Input:\s*(.+)", text, re.DOTALL)

    return (
        thought.group(1).strip() if thought else "",
        action.group(1).strip() if action else "",
        action_input.group(1).strip() if action_input else "",
    )


def _extract_thread_id(text: str) -> str | None:
    match = re.search(r'thread[_\s]?id["\s:]+([a-f0-9\-]{36})', text, re.IGNORECASE)
    return match.group(1) if match else None


def _needs_approval(text: str) -> bool:
    return "APPROVAL REQUIRED" in text.upper()


def _ask_user_approval(tool_output: str, get_input) -> bool:
    print("\n⚠️  APPROVAL REQUIRED")
    print("─" * 50)
    print(tool_output)
    print("─" * 50)
    answer = get_input("Approve this operation? [yes/no]: ").strip().lower()
    return answer in ("yes", "y")


# Maps common wrong arg names the LLM uses → correct parameter names per tool
_ARG_REMAP = {
    "ask_database":           {"query": "question", "input": "question", "text": "question"},
    "run_read_query":         {"query": "sql", "question": "sql", "input": "sql"},
    "explain_sql":            {"query": "sql", "question": "sql"},
    "preview_write_operation":{"query": "sql", "question": "sql"},
    "describe_database_table":{"table": "table_name", "name": "table_name"},
    "get_database_schema":    {"table": "table_names", "tables": "table_names"},
}


def _remap_args(tool_name: str, args: dict) -> dict:
    remap = _ARG_REMAP.get(tool_name, {})
    return {remap.get(k, k): v for k, v in args.items()}


def _parse_action_input(tool_name: str, action_input: str) -> dict:
    """Parse action_input into a dict, handling plain strings and JSON."""
    raw = action_input.strip()

    # Already valid JSON object
    if raw.startswith("{"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

    # Plain string — map to the first required param of the tool
    tool_fn = _tools_by_name.get(tool_name)
    if tool_fn and tool_fn.args:
        first_param = next(iter(tool_fn.args))
        return {first_param: raw}

    return {}


def _run_tool(tool_name: str, action_input: str, user_id: str, get_input) -> str:
    tool_fn = _tools_by_name.get(tool_name)
    if not tool_fn:
        return f"Unknown tool: {tool_name}"

    args = _remap_args(tool_name, _parse_action_input(tool_name, action_input))

    print(f"\n🔧 {tool_name}({', '.join(f'{k}={v}' for k, v in args.items())})")
    output = tool_fn.invoke(args)

    if _needs_approval(str(output)):
        thread_id = _extract_thread_id(str(output))
        approved = _ask_user_approval(str(output), get_input)

        if approved and thread_id:
            result = _tools_by_name["approve_operation"].invoke(
                {"thread_id": thread_id, "approved_by": user_id}
            )
            print(f"✅ Approved")
            return str(result)
        elif thread_id:
            result = _tools_by_name["reject_operation"].invoke(
                {"thread_id": thread_id, "reason": "User rejected"}
            )
            print("❌ Rejected")
            return str(result)

    return str(output)


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOllama(model=MODEL_NAME, base_url=OLLAMA_BASE_URL, temperature=0)
    return _llm


def run_agent(question: str, user_id: str = AGENT_USER_ID, get_input=input) -> str:
    log.info(f"Agent query: {question}")

    memories = search_memory(user_id, question)
    context = build_context_prompt(memories)
    system_content = REACT_SYSTEM + context

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=question),
    ]

    for iteration in range(MAX_ITERATIONS):
        log.debug(f"Iteration {iteration + 1}")
        response = get_llm().invoke(messages)
        text = response.content
        messages.append(AIMessage(content=text))

        thought, action, action_input = _parse_react(text)
        log.debug(f"Thought: {thought} | Action: {action}")

        if not action:
            log.info("No action parsed — returning raw response")
            add_memory(user_id, f"Q: {question}\nA: {text}")
            return text

        if action.strip().lower() in ("final answer", "finalanswer"):
            log.info("Agent reached Final Answer")
            add_memory(user_id, f"Q: {question}\nA: {action_input}")
            return action_input

        observation = _run_tool(action.strip(), action_input, user_id, get_input)
        log.debug(f"Observation: {observation[:200]}")
        messages.append(HumanMessage(content=f"Observation: {observation}"))

    log.warning("Max iterations reached")
    return "Max iterations reached. Please try a more specific question."
