# YouTube Video Summarizer 🎥

A local AI-powered app that takes a YouTube URL, downloads the audio, transcribes it using Whisper, and generates a concise summary using Llama 2 — all running on your machine with no external API calls.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Download audio from YouTube |
| [OpenAI Whisper](https://github.com/openai/whisper) | Speech-to-text transcription |
| [Haystack AI v2](https://haystack.deepset.ai/) | LLM pipeline orchestration |
| [Ollama](https://ollama.com/) | Run Llama 2 locally |
| [Gradio](https://gradio.app/) | Web UI |
| [ffmpeg](https://ffmpeg.org/) | Audio extraction (used by yt-dlp) |

---

## Project Structure

```
youtube_summarizer/
├── main.py            # Core logic: download, transcribe, summarize
├── app.py             # Gradio UI
├── requirements.txt   # Python dependencies
└── README.md
```

---

## Installation

1. Clone the repository:
   ```bash
   git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
   cd Awesome-AI-Agents
   git sparse-checkout set YouTube-Video-Summarization-Application
   git checkout
   cd YouTube-Video-Summarization-Application
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # Windows: env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install ffmpeg:
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg -y

   # macOS
   brew install ffmpeg
   ```

5. Install and start Ollama:
   ```bash
   # Install from https://ollama.com/download
   ollama pull llama2
   ollama serve
   ```

---

## Configuration

| Parameter | Location | Default | Options |
|---|---|---|---|
| Whisper model size | `main.py` → `transcribe_audio()` | `base` | `tiny`, `small`, `medium`, `large` |
| Ollama model | `main.py` → `summarize()` | `llama2` | any model pulled via `ollama pull` |
| Ollama URL | `main.py` → `summarize()` | `http://localhost:11434` | change if running Ollama remotely |

---

## Usage

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

2. Launch the app:
   ```bash
   python app.py
   ```

3. Open your browser at `http://127.0.0.1:7860`

4. Paste a YouTube URL and click **Summarize** — the transcript and summary will appear side by side.

---

## Notes

- All processing runs **fully locally** — no data is sent to external APIs
- Longer videos may exceed Llama 2's context window — chunking support is a planned improvement
- The downloaded `audio.mp3` is saved in the project root after each run
- For better transcription accuracy, switch Whisper from `base` to `small` or `medium` in `main.py`
- For better summaries, try `llama3` — `ollama pull llama3` and update `model_name` in `summarize()`

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) file for details.
