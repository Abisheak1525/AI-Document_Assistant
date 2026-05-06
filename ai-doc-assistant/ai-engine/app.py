from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import DocumentAssistant
import os

app = FastAPI()
assistant = DocumentAssistant()

# Auto-initialize the store on startup
assistant.load_vector_store()

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask(request: QueryRequest):
    try:
        # Use your existing logic
        answer = assistant.ask_question(request.query)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "online"}