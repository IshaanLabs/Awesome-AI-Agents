# AI PDF Chat

A simple AI-powered Retrieval Augmented Generation (RAG) application that lets you chat with your PDF documents using Ollama LLMs running locally or remotely. Upload multiple PDFs, index them into an in-memory Chroma vector store, and ask questions in a conversational chat interface powered by Streamlit.

---

## Tech Stack

| Tool                                                                        | Purpose                                                        |
| --------------------------------------------------------------------------- | -------------------------------------------------------------- |
| [Streamlit](https://streamlit.io/)                                             | Frontend UI                                                    |
| [streamlit-chat](https://pypi.org/project/streamlit-chat/)                     | Chat message UI components                                     |
| [LangChain](https://www.langchain.com/)                                        | RAG pipeline and LLM chaining                                  |
| [langchain-ollama](https://pypi.org/project/langchain-ollama/)                 | Ollama LLM and Embeddings wrapper                              |
| [langchain-community](https://pypi.org/project/langchain-community/)           | `PyPDFLoader`, `Chroma` vector store                       |
| [langchain-classic](https://pypi.org/project/langchain-classic/)               | `ConversationalRetrievalChain`, `ConversationBufferMemory` |
| [langchain-text-splitters](https://pypi.org/project/langchain-text-splitters/) | `RecursiveCharacterTextSplitter`                             |
| [Ollama](https://ollama.com/)                                                  | Local/remote LLM and embedding inference                       |
| [ChromaDB](https://www.trychroma.com/)                                         | In-memory vector store                                         |
| [pypdf](https://pypi.org/project/pypdf/)                                       | PDF parsing backend for PyPDFLoader                            |

---

## Project Structure

```
ai-pdf-chat/
├── app.py              # Streamlit UI
├── main.py             # RAG logic (LangChain + Ollama + Chroma)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## Installation

1. Clone the repository:

   ```bash
   git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
   cd Awesome-AI-Agents
   git sparse-checkout set ai-pdf-chat
   git checkout
   cd ai-pdf-chat
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

This app requires a running Ollama instance (local or remote) with both an LLM and an embedding model available.

- To run Ollama locally, install it from [https://ollama.com](https://ollama.com) and pull the required models:

  ```bash
  ollama pull mistral:7b-instruct-q5_K_M
  ollama pull all-minilm:l6-v2
  ```
- To use a remote Ollama instance, make sure the server is accessible and note its base URL (e.g. `http://192.168.x.x:11434`).

No `.env` file or API keys are needed — everything is configured directly in the sidebar.

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
   - Upload one or more **PDF files**
   - Click **Index Documents** to load, chunk, embed and store them in Chroma
   - Click **Clear Session** to reset the chat and vector store
3. In the main area:

   - Type your question in the input box and click **Send**
   - The app retrieves relevant chunks from the vector store and generates an answer
   - Full conversation history is maintained across questions

---

## Notes

- PDF files are loaded using LangChain's `PyPDFLoader`
- Text is split into chunks of 500 characters with 50 character overlap
- Embeddings are generated using Ollama's `all-minilm:l6-v2` model
- Vector store is created in-memory using Chroma — nothing is persisted to disk
- The retriever fetches the top 2 most relevant chunks per query (`k=2`)
- Conversation history is maintained using `ConversationBufferMemory`
- Uploaded files are saved temporarily and deleted after indexing

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) file for details.
