import sys
import os
from pathlib import Path

# Add project root to sys.path to allow importing from 'shared'
sys.path.append(str(Path(__file__).parent.parent))
from fastapi import FastAPI, UploadFile, File, HTTPException,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import engine, Base, get_db
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
import traceback
from services import IngestionService


# Add project root to sys.path to allow importing from 'shared'
sys.path.append(str(Path(__file__).parent.parent))

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  

app = FastAPI(
    title="Ingestion Service",
    description="Service for processing and indexing documents",
    lifespan=lifespan
)

PORT = 8001

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Ingestion Service",
        "status": "online",
        "message": "Welcome to the Document Ingestion API"
    }


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    
    print(f"\nReceived file: {file.filename}");
    
    if not file.filename.endswith(('.pdf', '.txt', '.docx')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    try:
        service = IngestionService(db)
        result = await service.process_file(file)  
        return {"status":"success","data":result}         
    except Exception as e:
        print("\n" + "!"*50)
        print("!!! ERROR IN INGESTION SERVICE !!!")
        traceback.print_exc()
        print("!"*50 + "\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def get_all_documents(db: AsyncSession = Depends(get_db)):
    try:
        service = IngestionService(db)
        documents = await service.get_all_documents()
        return {"status":"success","data":documents}
    except Exception as e:
        print("\n" + "!"*50)
        print("!!! ERROR IN INGESTION SERVICE !!!")
        traceback.print_exc()
        print("!"*50 + "\n")
        raise HTTPException(status_code=500, detail=str(e))
        
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
