from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import json

llm = ChatOllama(model="phi3:latest", temperature=0,base_url = "http:localhost:11434")  # Ensure this matches your Ollama server URL
print("Ollama LLM (phi3:latest) initialized.")

EXTRACT_PROMPT = PromptTemplate.from_template("""
Extract actionable tasks from this voice memo transcription.

Rules:
1. Output ONLY a JSON array, nothing else.
2. Each item must be an object with these exact keys: "title", "description", "priority", "status", "category"
3. priority must be one of: "high", "medium", "low"
4. status must always be: "todo"
5. category examples: "work", "personal", "health", "finance"
6. If no tasks found, return: []

Example output:
[{{"title": "Buy groceries", "description": "Get milk and eggs", "priority": "low", "status": "todo", "category": "personal"}}]

Transcription:
{transcription}

JSON array:
""")

chain = EXTRACT_PROMPT | llm


def extract_tasks(transcription):
    """Extract structured tasks from transcription text."""
    print("Extracting tasks from transcription...")

    response = chain.invoke({"transcription": transcription})
    content = response.content.strip()

    # Try to parse JSON from response
    try:
        # Handle markdown code blocks if present
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        tasks = json.loads(content)

        # Ensure each task is a dict with required fields
        valid_tasks = []
        for t in tasks:
            if isinstance(t, str):
                t = {"title": t, "description": "", "priority": "low", "status": "todo", "category": "general"}
            elif isinstance(t, dict):
                t.setdefault("title", "Untitled")
                t.setdefault("description", "")
                t.setdefault("priority", "low")
                t.setdefault("status", "todo")
                t.setdefault("category", "general")
            else:
                continue
            valid_tasks.append(t)

        print(f"Extracted {len(valid_tasks)} tasks.")
        return valid_tasks
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response: {content}")
        return []
