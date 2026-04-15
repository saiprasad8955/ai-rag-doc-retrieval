from datetime import datetime
import os
import shutil
import asyncio
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from shared.models import Document
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
UNIFIED_INDEX_PATH = f"{VECTOR_STORE_PATH}/unified_index"

class IngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " "]
        )

    async def process_file(self, file:UploadFile):
        print(f"Starting Processing file: {file.filename}")

        # 1. Save file temporarily
        temp_dir = "./temp_file_uploads"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        temp_file_path = f"{temp_dir}/{file.filename}"

        with open(temp_file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            def load_and_chunk():
                # 2. Load document based on type
                if file.filename.endswith(".pdf"):
                    loader = PyPDFLoader(temp_file_path)
                elif file.filename.endswith(".txt"):
                    loader = TextLoader(temp_file_path)
                else:
                    raise ValueError("Unsupported file type")
                documents = loader.load()
                return self.text_splitter.split_documents(documents)
                
            # 3. Create async task for embedding and indexing
            chunks = await asyncio.to_thread(load_and_chunk)
            print(f"Chunks created: {len(chunks)}")

            # 4. Add into Database
            new_doc = Document(
                filename=file.filename,
                upload_date= datetime.now(),
                content_type=file.content_type,
                metadata_info={"chunk_count":len(chunks)}
            )
            self.db.add(new_doc)
            await self.db.commit()
            await self.db.refresh(new_doc)

            # 5. Create Chroma Collection
            if not os.path.exists(UNIFIED_INDEX_PATH):
                os.makedirs(UNIFIED_INDEX_PATH)
                
            vector_store = Chroma(
                collection_name="all_documents_collection",
                embedding_function=self.embeddings,
                persist_directory=UNIFIED_INDEX_PATH
            )

            # 6. Add chunks to Chroma via async
            await asyncio.to_thread(vector_store.add_documents,chunks)
            print(f"Successfully indexed {len(chunks)} chunks")

            return {
                "message": "Document processed successfully",
                "document_id": new_doc.id,
                "chunks_indexed": len(chunks)
            }
            
        finally:
            # 7. Cleanup
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            print("Cleaned up temporary file")

    async def get_all_documents(self):
        result = await self.db.execute(select(Document))
        documents = result.scalars().all()
        return documents
                
                


                
            
        
        