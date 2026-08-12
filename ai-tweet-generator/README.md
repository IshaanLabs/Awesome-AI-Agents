# AI Tweet Generator

A simple AI-powered viral tweet generator that takes your idea as free text, extracts key topics using an Ollama LLM, performs a real-time web search using Tavily, and generates a catchy viral tweet with hashtags — all in a clean Streamlit UI.

---

## Tech Stack

| Tool                                                        | Purpose                           |
| ----------------------------------------------------------- | --------------------------------- |
| [Streamlit](https://streamlit.io/)                             | Frontend UI                       |
| [LangChain](https://www.langchain.com/)                        | Prompt templates and LLM chaining |
| [langchain-ollama](https://pypi.org/project/langchain-ollama/) | Ollama LLM wrapper for LangChain  |
| [langchain-core](https://pypi.org/project/langchain-core/)     | `PromptTemplate`                |
| [Ollama](https://ollama.com/)                                  | Local/remote LLM inference        |
| [Tavily](https://tavily.com/)                                  | Real-time web search API          |
| [tavily-python](https://pypi.org/project/tavily-python/)       | Tavily Python client              |

---

## Project Structure

```
ai-tweet-generator/
├── app.py              # Streamlit UI
├── main.py             # Topic extraction, web search and tweet generation logic
├── requirements.txt    # Python dependencies
└── README.md
```

---

## Installation

1. Clone the repository:

   ```bash
   git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
   cd Awesome-AI-Agents
   git sparse-checkout set ai-tweet-generator
   git checkout
   cd ai-tweet-generator
   ```
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

This app requires a running Ollama instance and a Tavily API key.

- To run Ollama locally, install it from [https://ollama.com](https://ollama.com) and pull a model:

  ```bash
  ollama pull llama3.2
  ```
- To use a remote Ollama instance, make sure the server is accessible and note its base URL (e.g. `http://192.168.x.x:11434`).
- Get your free Tavily API key at [https://tavily.com](https://tavily.com) and enter it in the sidebar.

No `.env` file needed — everything is configured directly in the sidebar.

---

## Usage

1. Start the Streamlit app:

   ```bash
   streamlit run app.py
   ```
2. In the sidebar:

   - Enter your **Ollama Base URL** (default: `http://localhost:11434`)
   - Click **Load Models** to fetch available models from the Ollama server
   - Select a model from the dropdown (or type one manually)
   - Enter your **Tavily API Key**
3. In the main area:

   - Type your idea or topic in the text area
   - Click **Generate Tweet**
   - The app will show:
     - **Extracted Topics** — key topics pulled from your text by the LLM
     - **Web Search Results** — latest context fetched from the web via Tavily per topic
     - **Generated Tweet** — one viral tweet with hashtags ready to copy and post

---

## Notes

- The LLM extracts 3 to 5 key topics from the user's input as a comma-separated list
- Tavily searches the web for each topic with `max_results=3` per topic
- The tweet is generated using the user's idea, extracted topics and web search context combined
- The tweet is constrained to 1000 characters with hashtags at the end
- The Tavily API key is entered as a password field and never stored

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) file for details.
