import whisper
from qdrant_client import QdrantClient, models
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from fastembed import SparseTextEmbedding

# ─── CONFIG ───────────────────────────────────────────────────────────────────

AUDIO_PATH        = "/mnt/d/Personal/Experiments/2026/awesome/chat_audios/Amazon_Rainforest__Tipping_Point_and_Global_Cost.wav"
COLLECTION_NAME   = "chat_audio"
DENSE_MODEL_NAME  = "BAAI/bge-large-en-v1.5"
SPARSE_MODEL_NAME = "prithivida/Splade_PP_en_v1"
OLLAMA_BASE_URL   = "http://localhost:11434"
OLLAMA_MODEL      = "llama2:latest"
QDRANT_URL        = "http://localhost:6333"
DENSE_DIM         = 1024   # bge-large-en-v1.5 output dim
BATCH_SIZE        = 32

# ─── STEP 1: TRANSCRIBE ───────────────────────────────────────────────────────

def transcribe(audio_path):
    print(f"[Transcribe] Loading whisper base model ...")
    model = whisper.load_model("base")

    print(f"[Transcribe] Transcribing {audio_path} ...")
    result = model.transcribe(audio_path)

    segments = result.get("segments", [])
    texts = [seg["text"].strip() for seg in segments if seg["text"].strip()]

    print(f"[Transcribe] Got {len(texts)} segments from audio.")
    return texts

# ─── STEP 2: EMBED (DENSE + SPARSE) ──────────────────────────────────────────

def load_embed_models():
    print(f"[Embed] Loading dense model: {DENSE_MODEL_NAME} ...")
    dense_model = HuggingFaceEmbedding(
        model_name=DENSE_MODEL_NAME,
        trust_remote_code=True,
        cache_folder="./hf_cache"
    )

    print(f"[Embed] Loading sparse model: {SPARSE_MODEL_NAME} ...")
    sparse_model = SparseTextEmbedding(model_name=SPARSE_MODEL_NAME)

    return dense_model, sparse_model


def embed_texts(texts, dense_model, sparse_model):
    print(f"[Embed] Generating dense embeddings for {len(texts)} chunks ...")
    dense_embeddings = dense_model.get_text_embedding_batch(texts)

    print(f"[Embed] Generating sparse embeddings for {len(texts)} chunks ...")
    sparse_embeddings = list(sparse_model.embed(texts, batch_size=BATCH_SIZE))

    print(f"[Embed] Done embedding.")
    return dense_embeddings, sparse_embeddings

# ─── STEP 3: QDRANT SETUP + INGEST ───────────────────────────────────────────

def setup_qdrant():
    print(f"[Qdrant] Connecting to {QDRANT_URL} ...")
    client = QdrantClient(url=QDRANT_URL)

    if not client.collection_exists(COLLECTION_NAME):
        print(f"[Qdrant] Creating collection: {COLLECTION_NAME} ...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "dense": models.VectorParams(
                    size=DENSE_DIM,
                    distance=models.Distance.DOT,
                    on_disk=True
                )
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            },
            optimizers_config=models.OptimizersConfigDiff(
                default_segment_number=5,
                indexing_threshold=0
            ),
            quantization_config=models.BinaryQuantization(
                binary=models.BinaryQuantizationConfig(always_ram=True)
            ),
        )
    else:
        print(f"[Qdrant] Collection '{COLLECTION_NAME}' already exists, skipping creation.")

    return client


def ingest(client, texts, dense_embeddings, sparse_embeddings):
    print(f"[Qdrant] Ingesting {len(texts)} points ...")

    points = []
    for i, (text, dense_vec, sparse_vec) in enumerate(zip(texts, dense_embeddings, sparse_embeddings)):
        points.append(
            models.PointStruct(
                id=i,
                vector={
                    "dense": dense_vec,
                    "sparse": models.SparseVector(
                        indices=sparse_vec.indices.tolist(),
                        values=sparse_vec.values.tolist()
                    )
                },
                payload={"text": text}
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)

    print(f"[Qdrant] Updating indexing threshold after ingest ...")
    client.update_collection(
        collection_name=COLLECTION_NAME,
        optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000)
    )
    print(f"[Qdrant] Ingest complete.")

# ─── STEP 4: HYBRID SEARCH ───────────────────────────────────────────────────

def hybrid_search(query, client, dense_model, sparse_model, top_k=3):
    print(f"[Search] Running hybrid search for: '{query}' ...")

    dense_vec = dense_model.get_query_embedding(query)
    sparse_vec = list(sparse_model.embed([query]))[0]

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            models.Prefetch(
                query=dense_vec,
                using="dense",
                limit=top_k * 2
            ),
            models.Prefetch(
                query=models.SparseVector(
                    indices=sparse_vec.indices.tolist(),
                    values=sparse_vec.values.tolist()
                ),
                using="sparse",
                limit=top_k * 2
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=top_k,
    )

    contexts = [point.payload["text"] for point in results.points]
    print(f"[Search] Retrieved {len(contexts)} context chunks.")
    return contexts

# ─── STEP 5: RAG ─────────────────────────────────────────────────────────────

def setup_llm():
    print(f"[LLM] Connecting to Ollama at {OLLAMA_BASE_URL} with model {OLLAMA_MODEL} ...")
    llm = Ollama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.7,
        context_window=4096,
    )
    return llm


def ask(query, client, dense_model, sparse_model, llm):
    contexts = hybrid_search(query, client, dense_model, sparse_model)

    context_str = "\n\n---\n\n".join(contexts)

    prompt = (
        "Context information is below.\n"
        "---------------------\n"
        f"{context_str}\n"
        "---------------------\n"
        "Using the context above, answer the query in a crisp manner. "
        "If you don't know, say 'I don't know!'.\n"
        f"Query: {query}\n"
        "Answer: "
    )

    print(f"[RAG] Sending query to LLM ...")
    response = llm.stream_complete(prompt)

    print(f"[RAG] Answer:\n")
    full_response = ""
    for chunk in response:
        print(chunk.delta, end="", flush=True)
        full_response += chunk.delta
    print("\n")

    return full_response

# ─── MAIN ─────────────────────────────────────────────────────────────────────

# if __name__ == "__main__":

#     # Step 1: Transcribe
#     texts = transcribe(AUDIO_PATH)

#     # Step 2: Load models + embed
#     dense_model, sparse_model = load_embed_models()
#     dense_embeddings, sparse_embeddings = embed_texts(texts, dense_model, sparse_model)

#     # Step 3: Setup Qdrant + ingest
#     client = setup_qdrant()
#     ingest(client, texts, dense_embeddings, sparse_embeddings)

#     # Step 4 + 5: Query loop
#     print("\n[Ready] You can now ask questions about the audio. Type 'exit' to quit.\n")
#     while True:
#         query = input("Your question: ").strip()
#         if query.lower() in ("exit", "quit"):
#             print("Bye!")
#             break
#         if not query:
#             continue
#         ask(query, client, dense_model, sparse_model, llm=setup_llm())
