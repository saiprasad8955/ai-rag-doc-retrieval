import traceback
import sys
from pathlib import Path

# Add project root to sys.path to allow importing from 'shared'
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services import QueryService
import uvicorn
import os
from shared.database import get_db

app = FastAPI(
    title="Query Service",
    description="Service for querying the document knowledge base",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    return {
        "service": "Query Service",
        "status": "online",
        "message": "Welcome to the Document Query API"
    }


@app.post("/query")
async def query_documents(request: QueryRequest):
    print(f"Received query: {request.question}")

    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required")

    
    try:
        print("[Step 1] Initializing QueryService...")
        service = QueryService()
        
        print("[Step 2] Processing query...")
        answer = await service.answer_question(request.question)
        
        print("[Step 3] Query processed successfully")
        return {
        "answer": answer,
        "message": "Query processing placeholder"
        }

    except Exception as e:
        print("\n" + "!"*50)
        print("!!! ERROR IN QUERY SERVICE !!!")
        traceback.print_exc()
        print("!"*50 + "\n")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
