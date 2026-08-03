# AI Email Generator

AI Email Generator is a Streamlit-based application that helps users draft polished emails from a short natural-language description. It uses an LLM through Ollama to generate an email subject and body, then allows users to refine the result with follow-up feedback.

## Tech Stack

- Python
- Streamlit
- LangChain
- Ollama
- python-dotenv

## Project Structure

- `app.py` — Streamlit frontend for the email generator UI
- `email_chain.py` — LLM prompt chain, email parsing, and revision logic
- `requirements.txt` — Python dependencies


---

## Installation

**1. Clone the repository**
```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set ai-email-generator
git checkout
cd ai-email-generator
```

**2. Install Python dependencies**
```bash
pip install -r requirements.txt
```


---

## Configuration

This project expects an Ollama instance to be running and configured with environment variables.

Create a `.env` file in the project root with the following values:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

Make sure the selected model is available in your Ollama setup.

## Usage

Run the app with:

```bash
streamlit run app.py
```

Then:

1. Enter a description of the email you want to create.
2. Click "Generate email".
3. Review the subject and body.
4. Use the feedback box to refine the draft further.

## Notes

- The app relies on Ollama for model inference, so Ollama must be installed and running locally.
- The generated emails are based on the provided brief and follow-up instructions.
- The app stores conversation state during the session for iterative edits.

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the MIT License file for details.
