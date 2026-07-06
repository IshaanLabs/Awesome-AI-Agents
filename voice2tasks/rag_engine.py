from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
import os

db_path = os.path.join(os.path.dirname(__file__), "chroma_db")

embeddings = OllamaEmbeddings(model="nomic-embed-text:latest", base_url="http:localhost:11434")
vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings, collection_name="voice_memos")
print("ChromaDB (via LangChain) ready.")

llm = ChatOllama(model="phi3:latest", temperature=0, base_url="http:localhost:11434")

RAG_PROMPT = PromptTemplate.from_template("""
You are a helpful assistant. Answer the user's question based on the context from their voice memos and tasks.

Context:
{context}

Question:
{question}

Answer concisely and helpfully:
""")

rag_chain = RAG_PROMPT | llm


def store_memo(memo_id, transcription, tasks_text):
    """Store transcription and tasks in ChromaDB."""
    print(f"Storing memo {memo_id} in ChromaDB...")
    doc = f"Transcription: {transcription}\n\nTasks: {tasks_text}"
    vectorstore.add_texts(texts=[doc], ids=[memo_id])
    print("Stored successfully.")


def query_memos(question):
    """Query stored memos using RAG."""
    print(f"RAG query: {question}")

    docs = vectorstore.similarity_search(question, k=3)

    if not docs:
        return "No relevant memos found. Try uploading some voice memos first."

    context = "\n\n---\n\n".join([doc.page_content for doc in docs])
    response = rag_chain.invoke({"context": context, "question": question})
    print("RAG response generated.")
    return response.content
