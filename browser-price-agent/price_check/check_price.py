"""
Price check v1: Haystack Agent + Ollama + Playwright MCP (real retailer page).

Tools: browser_navigate, browser_snapshot

Prereqs:
  1) Ollama reachable (OLLAMA_URL)
  2) bash price_agent/start_playwright_mcp.sh

Run:
  bash price_agent/run_price_check.sh
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from ollama import ResponseError

# --- config (change OLLAMA_URL later for remote) ---
OLLAMA_URL = "http://localhost:11434"
# qwen3.5:4b often emits broken tool-call XML -> Ollama 500.
OLLAMA_MODEL = "qwen2.5:7b"
MCP_URL = "http://localhost:8931/mcp"

# Real product page — Amazon often CAPTCHA-blocks headless Chrome.
# Logitech is OK for navigate/snapshot; avoid click tools (model invents stale refs).
PRODUCT_URL = "https://www.logitech.com/en-us/products/mice/mx-master-3s.html"

TOOL_NAMES = [
    "browser_navigate",
    "browser_snapshot",
]

SYSTEM_PROMPT = """
You are a price-check browser agent for retailer product pages.

Hard rules:
- Your FINAL message must be ONLY a markdown table with columns: Name | Price | URL
- Never write pros, cons, reviews, summaries, or explanations.
- Never answer from memory. Use tools first.
- Allowed tools only:
  - browser_navigate with {"url": "<page url>"}
  - browser_snapshot with NO arguments ({})
- Never pass target/selector/CSS/xpath/refs to any tool.
- Never call browser_click.
- Price = primary listed price from the snapshot.
- If CAPTCHA, login wall, or no price visible: Price = BLOCKED (still return the table).
""".strip()

def log(message: str) -> None:
    print(f"[price] {message}", flush=True)


def check_ollama() -> bool:
    log(f"Checking Ollama at {OLLAMA_URL} ...")
    tags_url = f"{OLLAMA_URL.rstrip('/')}/api/tags"
    try:
        with urllib.request.urlopen(tags_url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        log(f"Ollama NOT reachable: {exc}")
        return False
    except Exception as exc:  # noqa: BLE001
        log(f"Ollama check failed: {exc}")
        return False

    models = [m.get("name", "") for m in payload.get("models", [])]
    log(f"Ollama OK. Models found: {len(models)}")
    if not any(OLLAMA_MODEL in name for name in models):
        log(f"Model '{OLLAMA_MODEL}' not found.")
        return False
    log(f"Model '{OLLAMA_MODEL}' is available.")
    return True


def check_mcp() -> bool:
    log(f"Checking Playwright MCP at {MCP_URL} ...")
    base = MCP_URL.rsplit("/mcp", 1)[0]
    try:
        with urllib.request.urlopen(base, timeout=5) as response:
            log(f"MCP host responded with status {response.status}")
            return True
    except urllib.error.HTTPError as exc:
        log(f"MCP host is up (HTTP {exc.code}) — continuing.")
        return True
    except urllib.error.URLError as exc:
        log(f"Playwright MCP NOT reachable: {exc}")
        log("Start it with: bash price_agent/start_playwright_mcp.sh")
        return False
    except Exception as exc:  # noqa: BLE001
        log(f"MCP check failed: {exc}")
        return False


def make_toolset() -> MCPToolset:
    log(f"Creating MCPToolset with tools: {TOOL_NAMES}")
    server_info = StreamableHttpServerInfo(url=MCP_URL)
    toolset = MCPToolset(server_info=server_info, tool_names=TOOL_NAMES)
    log(f"Tools loaded: {[t.name for t in toolset.tools]}")
    return toolset


def make_agent(toolset: MCPToolset) -> Agent:
    log(f"Creating OllamaChatGenerator model={OLLAMA_MODEL} url={OLLAMA_URL}")
    # No streaming: avoids mid-stream XML parse crashes from Ollama/Qwen tool calls.
    # think=False: thinking models sometimes break tool-call markup.
    chat_generator = OllamaChatGenerator(
        model=OLLAMA_MODEL,
        url=OLLAMA_URL,
        think=False,
        generation_kwargs={"temperature": 0.0},
    )

    log("Creating Haystack Agent (no streaming)")
    agent = Agent(
        chat_generator=chat_generator,
        tools=toolset,
        system_prompt=SYSTEM_PROMPT,
        exit_conditions=["text"],
    )
    return agent


def build_prompt(product_url: str) -> str:
    return f"""
Task: extract product name + primary price from this product page.

Steps:
1. browser_navigate to: {product_url}
2. browser_snapshot with no arguments (do not pass target/selector/refs).
3. Reply with ONLY this table (one data row). No other text.

| Name | Price | URL |
|------|-------|-----|
| <name from page> | <price or BLOCKED> | {product_url} |
""".strip()


def is_valid_price_table(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    banned = ["pros:", "cons:", "### ", "overall rating", "based on the"]
    if any(b in lowered for b in banned):
        return False
    has_header = "| name | price | url |" in lowered
    has_sep = "|---" in text.replace(" ", "")
    rows = [line for line in text.strip().splitlines() if line.strip().startswith("|")]
    return has_header and has_sep and len(rows) >= 3


def log_messages(messages) -> None:
    log(f"Agent returned {len(messages)} messages")
    for i, msg in enumerate(messages):
        role = getattr(msg, "role", None)
        role_name = getattr(role, "value", str(role))
        tool_calls = getattr(msg, "tool_calls", None) or []
        text = getattr(msg, "text", None) or ""
        preview = (text[:160] + "...") if len(text) > 160 else text
        log(f"  msg[{i}] role={role_name} tool_calls={len(tool_calls)} text={preview!r}")
        for tc in tool_calls:
            log(f"    tool={tc.tool_name} args={tc.arguments}")


def run_agent_once(agent: Agent, messages: list) -> tuple:
    """Run agent once. Returns (result_dict_or_None, error_or_None)."""
    try:
        return agent.run(messages=messages), None
    except ValueError as exc:
        # Ollama/Qwen sometimes returns an empty assistant message after failed tools.
        log(f"Agent ValueError: {exc}")
        return None, exc


def run_price_check(agent: Agent) -> None:
    prompt = build_prompt(PRODUCT_URL)
    log(f"User prompt:\n{prompt}")

    log("Running agent (attempt 1) ...")
    result, err = run_agent_once(agent, [ChatMessage.from_user(prompt)])
    text = ""

    if result is not None:
        all_messages = result.get("messages") or []
        log_messages(all_messages)
        last = result.get("last_message")
        text = (getattr(last, "text", None) or "") if last else ""
        log(f"Attempt 1 valid_table={is_valid_price_table(text)}")
    else:
        log(f"Attempt 1 failed: {err}")

    if not is_valid_price_table(text):
        # Fresh conversation — do NOT reuse broken history with empty ChatMessages.
        log("Retrying with a fresh conversation (no prior history) ...")
        retry_prompt = (
            build_prompt(PRODUCT_URL)
            + "\n\nIMPORTANT: use only browser_navigate and browser_snapshot. "
            "Do not click. Final answer = markdown table only."
        )
        result, err = run_agent_once(agent, [ChatMessage.from_user(retry_prompt)])
        if result is not None:
            all_messages = result.get("messages") or []
            log_messages(all_messages)
            last = result.get("last_message")
            text = (getattr(last, "text", None) or "") if last else ""
            log(f"Attempt 2 valid_table={is_valid_price_table(text)}")
        else:
            log(f"Attempt 2 failed: {err}")
            text = (
                "| Name | Price | URL |\n"
                "|------|-------|-----|\n"
                f"| UNKNOWN | BLOCKED | {PRODUCT_URL} |"
            )

    log("--- PRICE CHECK RESULT ---")
    print(text, flush=True)
    log("--- END ---")
    if not is_valid_price_table(text):
        log("WARNING: final answer still not a valid price table.")


def main() -> None:
    log("Starting price check")
    log(f"Config OLLAMA_URL={OLLAMA_URL} MODEL={OLLAMA_MODEL} MCP_URL={MCP_URL}")
    log(f"Product URL={PRODUCT_URL}")

    if not check_ollama():
        log("Abort: Ollama not ready.")
        return
    if not check_mcp():
        log("Abort: Playwright MCP not ready.")
        return

    try:
        toolset = make_toolset()
        agent = make_agent(toolset)
        run_price_check(agent)
    except ResponseError as exc:
        log(f"Ollama tool-call error: {exc}")
        log(
            "This is usually the model emitting broken tool XML. "
            "Try OLLAMA_MODEL='qwen2.5:7b' or 'qwen3.5:9b-q4_K_M'."
        )
        raise
    except Exception as exc:  # noqa: BLE001
        log(f"Price check crashed: {exc}")
        raise
    finally:
        log("Price check script exiting.")


if __name__ == "__main__":
    main()
