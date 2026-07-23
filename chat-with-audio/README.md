# 🎙️ Chat with Audio

> Talk to your audio files using AI — transcribe, index, and chat with any audio recording using a fully local RAG pipeline.

---

## 📖 Description

**Chat with Audio** is a local AI-powered application that lets you upload any audio file and have a natural conversation about its contents. It transcribes the audio using OpenAI Whisper, indexes the transcript into a Qdrant vector database using hybrid search (dense + sparse embeddings), and answers your questions using a local LLM via Ollama — all through a clean, dark-themed Streamlit chat interface.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Transcription | [OpenAI Whisper](https://github.com/openai/whisper) (base model) |
| Dense Embeddings | [BAAI/bge-large-en-v1.5](https://huggingface.co/BAAI/bge-large-en-v1.5) via HuggingFace |
| Sparse Embeddings | [SPLADE](https://huggingface.co/prithivida/Splade_PP_en_v1) via FastEmbed |
| Vector Database | [Qdrant](https://qdrant.tech/) (local, Docker) |
| Hybrid Search | Qdrant RRF (Reciprocal Rank Fusion) |
| LLM | [Ollama](https://ollama.com/) — `llama2:latest` |
| UI | [Streamlit](https://streamlit.io/) + [streamlit-chat](https://github.com/AI-Yash/st-chat) |

---

## 📁 Project Structure

```
chat_with_audio/
├── main.py              # Core pipeline — transcribe, embed, ingest, search, RAG
├── app.py               # Streamlit UI
├── requirements.txt     # Python dependencies
├── hf_cache/            # HuggingFace model cache (auto-created)
└── README.md
```

---

## ⚙️ Installation


### 1. Clone the repository
```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set chat-with-audio
git checkout
cd chat-with-audio
```



### 2. Prerequisites

- Python 3.10+
- [Docker](https://docs.docker.com/engine/install/ubuntu/) (for Qdrant)
- [Ollama](https://ollama.com/download) with `llama2:latest` pulled

```bash
ollama pull llama2
```

### 3. Start Qdrant

```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

### 4. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration

All configuration is at the top of `main.py`:

```python
AUDIO_PATH        = "sample.mp3"          # Path to audio file (used in CLI mode)
COLLECTION_NAME   = "chat_audio"          # Qdrant collection name
DENSE_MODEL_NAME  = "BAAI/bge-large-en-v1.5"
SPARSE_MODEL_NAME = "prithivida/Splade_PP_en_v1"
OLLAMA_BASE_URL   = "http://localhost:11434"
OLLAMA_MODEL      = "llama2:latest"
QDRANT_URL        = "http://localhost:6333"
DENSE_DIM         = 1024
BATCH_SIZE        = 32
```

---

## 🚀 Usage

### Streamlit UI (recommended)

```bash
streamlit run app.py
```

1. Open `http://localhost:8501` in your browser
2. Upload an audio file (mp3, wav, m4a, ogg, flac) from the sidebar
3. Click **🚀 Process Audio** — transcription, embedding and indexing happens automatically
4. Start chatting in the input box at the bottom
5. Use **🗑️ Reset Chat** to clear the conversation

### CLI mode

```bash
python main.py
```

Update `AUDIO_PATH` in `main.py` to point to your audio file before running.

---

## 📝 Notes

- First run will download the BGE and SPLADE models (~1.5GB total) into `./hf_cache`
- Whisper `base` model balances speed and accuracy — swap to `small` or `medium` in `main.py` for better transcription quality
- Uploading a new audio file **replaces** the existing collection and **resets** the chat
- Qdrant uses binary quantization + on-disk storage for memory efficiency
- The Ollama base URL can be pointed to a remote machine if needed

---

## 🤝 Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the MIT License — see the [MIT License](https://opensource.org/licenses/MIT) file for details.
