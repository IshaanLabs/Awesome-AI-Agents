# tools.py
# All tool functions the agent can call, plus their schemas (what the LLM sees).
# Each function does one real thing. Results are always returned as strings
# because that's what the LLM expects back from a tool call.

import json
import requests
from datetime import datetime
from pathlib import Path

from config import (
    TAVILY_API_KEY,
    TAVILY_SEARCH_URL,
    OPEN_METEO_GEOCODING_URL,
    OPEN_METEO_FORECAST_URL,
)


# --- Tool 1: Current Date ---

def get_current_date() -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"  [get_current_date] returning: {now}")
    return now


# --- Tool 2: Calculator ---

def calculate(expression: str) -> str:
    print(f"  [calculate] evaluating: {expression}")
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        print(f"  [calculate] result: {result}")
        return str(result)
    except Exception as e:
        print(f"  [calculate] error: {e}")
        return f"Error: {e}"


# --- Tool 3: Weather via Open-Meteo ---

def get_weather(city: str) -> str:
    print(f"  [get_weather] fetching weather for: {city}")
    try:
        # Step 1: geocode the city name to lat/lon
        geo_resp = requests.get(
            OPEN_METEO_GEOCODING_URL,
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        geo_data = geo_resp.json()

        if not geo_data.get("results"):
            return f"Could not find location: {city}"

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        name = location["name"]
        country = location.get("country", "")
        print(f"  [get_weather] resolved to: {name}, {country} ({lat}, {lon})")

        # Step 2: fetch current weather
        weather_resp = requests.get(
            OPEN_METEO_FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weathercode,windspeed_10m",
                "temperature_unit": "celsius",
                "windspeed_unit": "kmh",
                "timezone": "auto",
            },
            timeout=10,
        )
        weather_data = weather_resp.json()
        current = weather_data["current"]

        temp = current["temperature_2m"]
        wind = current["windspeed_10m"]
        code = current["weathercode"]

        # Map WMO weather code to a human-readable description
        description = _wmo_code_to_description(code)

        result = f"Weather in {name}, {country}: {temp}°C, {description}, wind {wind} km/h"
        print(f"  [get_weather] result: {result}")
        return result

    except Exception as e:
        print(f"  [get_weather] error: {e}")
        return f"Error fetching weather: {e}"


def _wmo_code_to_description(code: int) -> str:
    # WMO weather interpretation codes (subset)
    codes = {
        0: "clear sky",
        1: "mainly clear", 2: "partly cloudy", 3: "overcast",
        45: "fog", 48: "icy fog",
        51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
        61: "slight rain", 63: "moderate rain", 65: "heavy rain",
        71: "slight snow", 73: "moderate snow", 75: "heavy snow",
        80: "slight showers", 81: "moderate showers", 82: "violent showers",
        95: "thunderstorm", 96: "thunderstorm with hail",
    }
    return codes.get(code, f"weather code {code}")


# --- Tool 4: Web Search via Tavily ---

def web_search(query: str) -> str:
    print(f"  [web_search] searching for: {query}")
    try:
        resp = requests.post(
            TAVILY_SEARCH_URL,
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic",
                "max_results": 3,
            },
            timeout=15,
        )
        data = resp.json()

        if "results" not in data:
            return f"No results found for: {query}"

        results = []
        for i, r in enumerate(data["results"], 1):
            results.append(f"{i}. {r['title']}\n   {r['url']}\n   {r['content'][:200]}")

        output = "\n\n".join(results)
        print(f"  [web_search] got {len(data['results'])} results")
        return output

    except Exception as e:
        print(f"  [web_search] error: {e}")
        return f"Error during web search: {e}"


# --- Tool 5: Read File ---

def read_file(path: str) -> str:
    print(f"  [read_file] reading: {path}")
    try:
        file_path = Path(path).resolve()
        if not file_path.exists():
            return f"File not found: {path}"
        content = file_path.read_text(encoding="utf-8")
        print(f"  [read_file] read {len(content)} chars")
        return content
    except Exception as e:
        print(f"  [read_file] error: {e}")
        return f"Error reading file: {e}"


# --- Tool 6: Write File ---

def write_file(path: str, content: str) -> str:
    print(f"  [write_file] writing to: {path}")
    try:
        file_path = Path(path).resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        print(f"  [write_file] wrote {len(content)} chars")
        return f"Successfully wrote {len(content)} chars to '{path}'"
    except Exception as e:
        print(f"  [write_file] error: {e}")
        return f"Error writing file: {e}"


# --- Tool Registry ---
# Maps tool name (string) -> actual function.
# agent.py uses this to dispatch tool calls from the LLM.

TOOL_FUNCTIONS = {
    "get_current_date": get_current_date,
    "calculate": calculate,
    "get_weather": get_weather,
    "web_search": web_search,
    "read_file": read_file,
    "write_file": write_file,
}


# --- Tool Schemas ---
# JSON schemas passed to the LLM so it knows what tools exist,
# what each one does, and what arguments to pass.

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Returns the current date and time",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluates a math expression and returns the result",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A Python math expression, e.g. '2 + 2' or '100 * 0.15'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Gets current weather for a city using Open-Meteo",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name, e.g. 'Tokyo'"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches the web for a query and returns top results",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads and returns the content of a file from disk",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative file path"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes content to a file on disk, creating it if it doesn't exist",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative file path"},
                    "content": {"type": "string", "description": "The content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
]
