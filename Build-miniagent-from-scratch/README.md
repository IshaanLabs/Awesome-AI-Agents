# Build Mini Agent from Scratch

A minimal AI agent built from scratch using the **ReAct (Reason + Act)** pattern — no frameworks, no magic, just a deterministic loop. The agent accepts a plain English task, reasons about what to do, calls real tools, observes the results, and loops until it has a final answer.

---

## Tech Stack

| Technology                        | Purpose                                       |
| --------------------------------- | --------------------------------------------- |
| Python 3.11+                      | Core language                                 |
| [Ollama](https://ollama.com)         | Local LLM runtime (runs `qwen2.5` offline)  |
| `openai` SDK                    | Talks to Ollama via its OpenAI-compatible API |
| `requests`                      | HTTP calls to Open-Meteo and Tavily           |
| [Open-Meteo](https://open-meteo.com) | Free weather API — no key required           |
| [Tavily](https://tavily.com)         | Real web search API                           |

---

## Project Structure

```
Build-miniagent-from-scratch/
├── config.py          # All settings: Ollama, Tavily, Open-Meteo
├── tools.py           # 6 tool functions + schemas for the LLM
├── agent.py           # The ReAct loop — the entire agent architecture
├── main.py            # Entry point — wires client + agent + REPL
├── requirements.txt   # Python dependencies
└── README.md
```

---

## Installation

**1. Clone the repository**

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set Build-miniagent-from-scratch
git checkout
cd Build-miniagent-from-scratch
```

**2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**3. Install Ollama and pull the model**

Download Ollama from [ollama.com](https://ollama.com), then:

```bash
ollama pull qwen2.5
ollama serve
```

> `qwen2.5` is used because it reliably supports structured tool calling. Not all local models do.

---

## Configuration

Open `config.py` and update the following:

```python
# Ollama — no changes needed if running locally on default port
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL    = "qwen2.5"

# Tavily — replace with your key from tavily.com
TAVILY_API_KEY  = "tvly-your-api-key-here"
```

Open-Meteo requires no API key and works out of the box.

---

## Usage

```bash
python main.py
```

The agent starts an interactive REPL. Type any task in plain English.

---

### Example 1 — Weather query (agent infers the city)

```
You: How is the weather

==================================================
Task: How is the weather
Model: granite4.1:3b
==================================================

--- Iteration 1 ---
  [agent] sending messages to LLM...
  [agent] LLM requested 1 tool call(s)

  > calling tool: get_weather  args: {'city': 'New York'}
  [get_weather] fetching weather for: New York
  [get_weather] resolved to: New York, United States (40.71427, -74.00597)
  [get_weather] result: Weather in New York, United States: 21.2°C, mainly clear, wind 15.9 km/h

  [agent] all tools executed — looping back to LLM...

--- Iteration 2 ---
  [agent] sending messages to LLM...
  [agent] LLM returned final answer — done.

Answer: The current weather in New York, United States is 21.2°C with mostly clear
        conditions and a wind speed of 15.9 km/h.
```

---

### Example 2 — Weather for a specific city

```
You: I wanted weather for delhi

--- Iteration 1 ---
  [agent] sending messages to LLM...
  [agent] LLM requested 1 tool call(s)

  > calling tool: get_weather  args: {'city': 'Delhi'}
  [get_weather] fetching weather for: Delhi
  [get_weather] resolved to: Delhi, India (28.65195, 77.23149)
  [get_weather] result: Weather in Delhi, India: 22.5°C, clear sky, wind 0.9 km/h

  [agent] all tools executed — looping back to LLM...

--- Iteration 2 ---
  [agent] sending messages to LLM...
  [agent] LLM returned final answer — done.

Answer: The current weather in Delhi is 22.5°C with a clear sky and a wind speed of 0.9 km/h.
```

---

### Example 3 — Multi-step: web search → write result to file

The agent searches the web, composes a Twitter post from the results, and dumps it to a `.txt` file — all in one instruction.

```
You: I want you to search about the latest incident of bypassing firewalls, AI Agent
     accessed data of indian firms....CERT-IN and create a twitter post for me....
     dump in a txt file

--- Iteration 1 ---
  [agent] sending messages to LLM...
  [agent] LLM requested 1 tool call(s)

  > calling tool: web_search  args: {'query': 'latest incident bypassing firewalls CERT-IN AI Agent accessed data of Indian firms'}
  [web_search] searching for: latest incident bypassing firewalls CERT-IN AI Agent accessed data of Indian firms
  [web_search] got 3 results

  [agent] all tools executed — looping back to LLM...

--- Iteration 2 ---
  [agent] sending messages to LLM...
  [agent] LLM requested 1 tool call(s)

  > calling tool: write_file  args: {'path': 'twitter_post.txt', 'content': 'The latest breach saw AI agents bypassing firewalls and accessing sensitive data of multiple Indian firms, raising serious cybersecurity concerns. #CERTIn #CyberSecurity'}
  [write_file] writing to: twitter_post.txt
  [write_file] wrote 169 chars

  [agent] all tools executed — looping back to LLM...

--- Iteration 3 ---
  [agent] sending messages to LLM...
  [agent] LLM returned final answer — done.

Answer: The Twitter post has been created in twitter_post.txt:

  "The latest breach saw AI agents bypassing firewalls and accessing sensitive
  data of multiple Indian firms, raising serious cybersecurity concerns.
  #CERTIn #CyberSecurity"
```

> The agent ran 3 iterations: search → write file → final answer. Each loop built on the previous one.

## Available Tools

| Tool                 | What it does                                          |
| -------------------- | ----------------------------------------------------- |
| `get_current_date` | Returns the current date and time                     |
| `calculate`        | Safely evaluates a math expression                    |
| `get_weather`      | Fetches real weather for any city via Open-Meteo      |
| `web_search`       | Searches the web via Tavily and returns top 3 results |
| `read_file`        | Reads a file from disk                                |
| `write_file`       | Writes content to a file on disk                      |

---

## Contributing

Contributions are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License — see the [MIT License](https://opensource.org/licenses/MIT) for details.
