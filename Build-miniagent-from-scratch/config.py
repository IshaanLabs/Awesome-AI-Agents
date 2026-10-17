# config.py
# Central place for all configuration, keys, URLs, and model settings.
# Every other file imports from here — nothing is hardcoded elsewhere.

# --- Ollama ---
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"          # required by openai SDK, ignored by Ollama
OLLAMA_MODEL = "qwen2.5"           # best local model for tool calling
# OLLAMA_MODEL = "granite4.1:3b" 

# --- Tavily Web Search ---
TAVILY_API_KEY = "<Your-Tavily-Key>"  # replace with your key from tavily.com
TAVILY_SEARCH_URL = "https://api.tavily.com/search"

# --- Open-Meteo Weather (free, no key needed) ---
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
