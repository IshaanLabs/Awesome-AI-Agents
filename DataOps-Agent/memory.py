import sys
sys.path.insert(0, "/mnt/d/awesome/SQL_AI/DataOps-Agent")
sys.path.append("/mnt/d/awesome/SQL_AI")

from mem0 import Memory
from config import QDRANT_HOST, QDRANT_PORT, OLLAMA_BASE_URL, EMBEDDING_MODEL_NAME, MODEL_NAME
from logger import get_logger

log = get_logger("memory")

MEM0_CONFIG = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QDRANT_HOST,
            "port": QDRANT_PORT,
            "collection_name": "dataops_agent",
            "embedding_model_dims": 768,
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": EMBEDDING_MODEL_NAME,
            "ollama_base_url": OLLAMA_BASE_URL,
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": MODEL_NAME,
            "ollama_base_url": OLLAMA_BASE_URL,
        },
    },
}

_memory = None


def get_memory() -> Memory:
    global _memory
    if _memory is None:
        log.info("Initializing Mem0 with Qdrant backend")
        _memory = Memory.from_config(MEM0_CONFIG)
    return _memory


def add_memory(user_id: str, content: str) -> None:
    try:
        get_memory().add(content, user_id=user_id)
        log.debug(f"Memory added for {user_id}")
    except Exception as e:
        log.warning(f"Memory add failed: {e}")


def search_memory(user_id: str, query: str, limit: int = 5) -> list[str]:
    try:
        results = get_memory().search(query, filters={"user_id": user_id}, limit=limit)
        memories = results.get("results", []) if isinstance(results, dict) else results
        return [m.get("memory", "") for m in memories if m.get("memory")]
    except Exception as e:
        log.warning(f"Memory search failed: {e}")
        return []


def get_recent_memory(user_id: str, limit: int = 5) -> list[str]:
    try:
        results = get_memory().get_all(user_id=user_id)
        memories = results.get("results", []) if isinstance(results, dict) else results
        return [m.get("memory", "") for m in memories[-limit:] if m.get("memory")]
    except Exception as e:
        log.warning(f"Memory fetch failed: {e}")
        return []
