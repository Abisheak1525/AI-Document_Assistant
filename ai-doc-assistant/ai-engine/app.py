from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import DocumentAssistant
import os
from fastapi import UploadFile, File
import shutil, os

app = FastAPI()
assistant = DocumentAssistant()

# Auto-initialize the store on startup
assistant.load_vector_store()

class QueryRequest(BaseModel):
    query: str

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    save_path = f"./uploaded_docs/{file.filename}"
    os.makedirs("./uploaded_docs", exist_ok=True)
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # TODO: Add your PDF indexing logic here (e.g. LangChain, ChromaDB)
    
    return {"status": "success", "filename": file.filename}

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