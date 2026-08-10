from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationalRetrievalChain
import tempfile
import os
import requests


def get_ollama_models(base_url):
    print(f"Fetching models from {base_url}...")
    try:
        response = requests.get(f"{base_url}/api/tags")
        response.raise_for_status()
        models = [model["name"] for model in response.json().get("models", [])]
        print(f"Found models: {models}")
        return models
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []


def load_documents(uploaded_files):
    print(f"Loading {len(uploaded_files)} PDF file(s)...")
    all_docs = []
    tmp_paths = []
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_paths.append(tmp.name)
        print(f"Loading: {uploaded_file.name}")
        loader = PyPDFLoader(tmp_paths[-1])
        docs = loader.load()
        all_docs.extend(docs)
    print(f"Total pages loaded: {len(all_docs)}")
    return all_docs, tmp_paths


def split_text_into_chunks(documents):
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    text_chunks = text_splitter.split_documents(documents)
    print(f"Total chunks: {len(text_chunks)}")
    return text_chunks


def create_embeddings(base_url):
    print("Creating Ollama embeddings with all-minilm:l6-v2 model...")
    embeddings = OllamaEmbeddings(model="all-minilm:l6-v2", base_url=base_url)
    print("Embeddings model ready.")
    return embeddings


def create_vector_store(text_chunks, embeddings):
    print("Creating in-memory Chroma vector store...")
    vector_store = Chroma.from_documents(text_chunks, embeddings)
    print("Vector store ready.")
    return vector_store


def load_llm(base_url, model_name):
    print(f"Loading LLM: {model_name} from {base_url}...")
    llm = OllamaLLM(model=model_name, base_url=base_url)
    print("LLM loaded.")
    return llm


def create_chain(llm, vector_store):
    print("Creating conversational retrieval chain...")
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
        memory=memory
    )
    print("Chain ready.")
    return chain


def conversation_chat(chain, query, history):
    print(f"User query: {query}")
    result = chain.invoke({"question": query, "chat_history": history})
    history.append((query, result["answer"]))
    print(f"Answer: {result['answer']}")
    return result["answer"]
