import sys
import os
from pathlib import Path

# Add project root to sys.path to allow importing from 'shared'
sys.path.append(str(Path(__file__).parent.parent))

from shared.database import Base
from shared.database import engine
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(
    title="Ingestion Service",
    description="Service for processing and indexing documents",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {
        "service": "Ingestion Service",
        "status": "online",
        "message": "Welcome to the Document Ingestion API"
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    
    
    if not file.filename.endswith(('.pdf', '.txt', '.docx')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "status": "received"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
