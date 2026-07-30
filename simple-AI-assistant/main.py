from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import ollama

app = FastAPI()
DEFAULT_MODEL = "llama3.2"

class ChatRequest(BaseModel):
    messages: list[dict]
    model: str = DEFAULT_MODEL

@app.get("/")
def index():
    return FileResponse("index.html")

@app.get("/models")
def get_models():
    return {"models": [m.model for m in ollama.list().models]}

@app.post("/chat")
def chat(req: ChatRequest):
    def stream():
        for chunk in ollama.chat(model=req.model, messages=req.messages, stream=True):
            token = chunk.message.content
            if token:
                yield token
    return StreamingResponse(stream(), media_type="text/plain")
