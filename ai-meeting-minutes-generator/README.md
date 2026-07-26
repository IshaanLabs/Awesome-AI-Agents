# 📝 AI Meeting Minutes Generator

> Automatically transform raw meeting transcripts into structured, professional Minutes of Meeting (MOM) documents — powered by open-source LLMs running locally via Ollama.

---

## About

**AI Meeting Minutes Generator** is a local, privacy-first tool that takes a raw meeting transcript and produces a comprehensive, well-structured MOM document in Markdown format.

Instead of relying on a single large prompt, the pipeline uses **prompt chaining** — breaking the task into 10 focused steps, each handled by a dedicated LLM call. This approach significantly improves accuracy and output quality compared to a single monolithic prompt.

The entire pipeline runs locally using [Ollama](https://ollama.com), meaning your meeting data never leaves your machine.

---

## Tech Stack

| Layer         | Technology                          |
| ------------- | ----------------------------------- |
| UI            | [Streamlit](https://streamlit.io)      |
| LLM Framework | [LangChain](https://www.langchain.com) |
| LLM Runtime   | [Ollama](https://ollama.com)           |
| Model         | `qwen2.5:7b-instruct-q4_K_M`      |
| Language      | Python 3.10+                        |

---

## Project Structure

```
ai-meeting-minutes-generator/
├── app.py               # Streamlit UI with step-by-step progress
├── mom_generator.py     # Prompt chaining pipeline (10 steps)
├── requirements.txt     # Python dependencies
├── output/              # Generated MOM markdown files (auto-created)
└── README.md
```

---

## Installation

**1. Clone the repository**

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set ai-meeting-minutes-generator
git checkout
cd ai-meeting-minutes-generator


```

**2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**3. Install Ollama and pull the model**

```bash
# Install Ollama from https://ollama.com
ollama pull qwen2.5:7b-instruct-q4_K_M
```

---

## Configuration

Open `mom_generator.py` and update the following constants at the top of the file:

```python
MODEL_NAME = "qwen2.5:7b-instruct-q4_K_M"   # Change to any Ollama model you prefer
BASE_URL   = "http://localhost:11434"          # Default Ollama URL, update if using a remote instance
OUTPUT_DIR = "output"                          # Folder where generated .md files are saved
```

---

## Usage

**1. Start the app**

```bash
streamlit run app.py
```

**2. Paste your transcript**

Open your browser at `http://localhost:8501`, paste your raw meeting transcript into the text area, and click **Generate MOM**.

**3. Review and download**

The app will process the transcript through 10 steps and display:

- A rendered **Preview** of the MOM
- The **Raw Markdown** you can copy
- A **Download button** to save the `.md` file

Generated files are also automatically saved to the `output/` folder with a timestamp, e.g. `MOM_20260726_143022.md`.

---

## How It Works

The pipeline chains 10 focused LLM calls, each responsible for one section of the MOM:

| Step | Task                                                            |
| ---- | --------------------------------------------------------------- |
| 1    | Clean transcript — remove noise, fillers, incomplete sentences |
| 2    | Extract metadata — attendees, date, meeting type               |
| 3    | Extract key discussion topics                                   |
| 4    | Generate executive summary                                      |
| 5    | Extract decisions made                                          |
| 6    | Extract action items                                            |
| 7    | Identify risks and open questions                               |
| 8    | Extract technical requirements and assumptions                  |
| 9    | Generate next steps                                             |
| 10   | Assemble final MOM document                                     |

Each step passes its output as context to the next, ensuring coherence across the full document.

---

## Notes

- The model runs **fully locally** — no data is sent to any external API
- Generation takes **1 to 3 minutes** depending on your hardware, since 10 LLM calls are made sequentially
- You can swap `qwen2.5:7b-instruct-q4_K_M` for any other Ollama-supported model by updating `MODEL_NAME` in `mom_generator.py`
- If you are using a remote Ollama instance, update `BASE_URL` accordingly
- Output quality depends on the transcript quality — cleaner transcripts produce better MOMs

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License — see the [MIT License](https://opensource.org/licenses/MIT) file for details.
