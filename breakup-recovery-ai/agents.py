import base64
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools import DuckDuckGoSearchRun

# ── Configuration ────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME      = "qwen2.5vl:7b"


# ── Helpers ───────────────────────────────────────────────────────────────────
def _build_llm() -> ChatOllama:
    return ChatOllama(model=MODEL_NAME, base_url=OLLAMA_BASE_URL)


def _encode_images(image_paths: list[str]) -> list[dict]:
    """Convert local image paths to base64 content blocks."""
    blocks = []
    for path in image_paths:
        try:
            data = Path(path).read_bytes()
            b64  = base64.b64encode(data).decode("utf-8")
            ext  = Path(path).suffix.lstrip(".").lower()
            mime = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"
            blocks.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})
            print(f"[agents] Encoded image: {path}")
        except Exception as e:
            print(f"[agents] ERROR - Failed to encode image {path}: {e}")
    return blocks


def _build_message(system: str, prompt: str, image_paths: list[str]) -> list:
    image_blocks = _encode_images(image_paths)
    content = [{"type": "text", "text": prompt}] + image_blocks
    return [SystemMessage(content=system), HumanMessage(content=content)]


# ── Agents ────────────────────────────────────────────────────────────────────
def therapist_agent(text: str, image_paths: list[str]) -> str:
    print("[agents] Therapist agent started")
    llm = _build_llm()

    system = (
        "You are an empathetic therapist. "
        "Listen with empathy, validate feelings, use gentle humor to lighten the mood, "
        "share relatable breakup experiences, and offer comforting encouragement. "
        "Analyze both text and any provided images for emotional context. "
        "Respond in markdown."
    )
    prompt = f"""Analyze the emotional state and provide empathetic support.

User's message: {text}

Provide:
1. Validation of feelings
2. Gentle words of comfort
3. Relatable experiences
4. Words of encouragement"""

    messages = _build_message(system, prompt, image_paths)
    response = llm.invoke(messages)
    print("[agents] Therapist agent completed")
    return response.content


def closure_agent(text: str, image_paths: list[str]) -> str:
    print("[agents] Closure agent started")
    llm = _build_llm()

    system = (
        "You are a closure specialist. "
        "Create emotional messages for unsent feelings, help express raw honest emotions, "
        "format messages clearly with headers, and ensure tone is heartfelt and authentic. "
        "Respond in markdown."
    )
    prompt = f"""Help create emotional closure based on the user's situation.

User's feelings: {text}

Provide:
1. Template for unsent messages
2. Emotional release exercises
3. Closure rituals
4. Moving forward strategies"""

    messages = _build_message(system, prompt, image_paths)
    response = llm.invoke(messages)
    print("[agents] Closure agent completed")
    return response.content


def routine_planner_agent(text: str, image_paths: list[str]) -> str:
    print("[agents] Routine planner agent started")
    llm = _build_llm()

    system = (
        "You are a recovery routine planner. "
        "Design 7-day recovery challenges, include fun activities and self-care tasks, "
        "suggest social media detox strategies, and create empowering playlists. "
        "Focus on practical recovery steps. Respond in markdown."
    )
    prompt = f"""Design a 7-day recovery plan based on the user's current state.

Current state: {text}

Include:
1. Daily activities and challenges
2. Self-care routines
3. Social media detox guidelines
4. Mood-lifting music suggestions"""

    messages = _build_message(system, prompt, image_paths)
    response = llm.invoke(messages)
    print("[agents] Routine planner agent completed")
    return response.content


def brutal_honesty_agent(text: str, image_paths: list[str]) -> str:
    print("[agents] Brutal honesty agent started")
    llm    = _build_llm()
    search = DuckDuckGoSearchRun()

    # Search for relevant advice to ground the response
    try:
        search_query  = f"how to move on after breakup advice psychology"
        search_result = search.run(search_query)
        print("[agents] DuckDuckGo search completed")
    except Exception as e:
        print(f"[agents] ERROR - DuckDuckGo search failed: {e}")
        search_result = "No search results available."

    system = (
        "You are a direct feedback specialist. "
        "Give raw, objective feedback about breakups, explain relationship failures clearly, "
        "use blunt factual language, and provide strong reasons to move forward. "
        "Do not sugar-coat. Respond in markdown."
    )
    prompt = f"""Provide honest, constructive feedback about the situation.

Situation: {text}

Relevant insights from the web:
{search_result}

Include:
1. Objective analysis of the situation
2. Growth opportunities
3. Future outlook
4. Actionable steps to move forward"""

    messages = _build_message(system, prompt, image_paths)
    response = llm.invoke(messages)
    print("[agents] Brutal honesty agent completed")
    return response.content
