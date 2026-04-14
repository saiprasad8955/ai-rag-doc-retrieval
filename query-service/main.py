import sys
from pathlib import Path

# Add project root to sys.path to allow importing from 'shared'
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

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
    top_k: int = 5

@app.get("/")
async def root():
    return {
        "service": "Query Service",
        "status": "online",
        "message": "Welcome to the Document Query API"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/query")
async def query_documents(request: QueryRequest):
    # Placeholder for querying logic
    return {
        "question": request.question,
        "results": [],
        "message": "Query processing placeholder"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
