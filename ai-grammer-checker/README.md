# AI Grammar Checker — Powered by Ollama + Streamlit

An LLM-powered web application that improves grammar, spelling, punctuation, and writing clarity using locally hosted or remote Ollama models. The application provides a simple Streamlit interface where users can enter text, select an available model, and receive a polished version while preserving the original meaning.

---

## Tech Stack

| Tool         | Purpose                              |
| ------------ | ------------------------------------ |
| Python 3.10+ | Core language                        |
| Streamlit    | Interactive web UI                   |
| Requests     | HTTP communication with Ollama       |
| Ollama       | Local or remote LLM inference server |

**Supported Models:**

- `llama3.2`
- Any model available through the connected Ollama server

---

## Project Structure

```text
ai-grammar-checker/
├── app.py              # Streamlit application and user interface
├── main.py              # Functions for communicating with Ollama and Prompt template for grammar correction
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation

```

## Installation

### 1. Clone the repository

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set ai-grammer-checker
git checkout
cd ai-grammer-checker
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the environment:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Ollama

Make sure Ollama is running.

```bash
ollama serve
```

Pull a model if you don't already have one.

```bash
ollama pull llama3.2
```

---

## Configuration

By default, the application connects to:

```text
http://localhost:11434
```

The Ollama URL can also be changed directly from the Streamlit interface, allowing the application to connect to remote Ollama servers.

---

## Usage

Start the Streamlit application.

```bash
streamlit run app.py
```

The application will open in your browser.

### Workflow

1. Enter the Ollama server URL.
2. Click **Refresh Models**.
3. Select a model from the dropdown.
4. Paste or type the text to improve.
5. Click **Correct Grammar**.
6. View the corrected text.

---

## Example

### Input

```text
he dont likes playing cricket because it rain yesterday.
```

### Output

```text
He doesn't like playing cricket because it rained yesterday.
```

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License — see the [MIT License](https://opensource.org/licenses/MIT) file for details.
