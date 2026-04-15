import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
UNIFIED_INDEX_PATH = f"{VECTOR_STORE_PATH}/unified_index"

class QueryService:
    def __init__(self):
        print(f"[Step 1] Initializing QueryService...")
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        print(f"[Step 2] Initializing Vector Store...")
        self.vector_store = Chroma(
            collection_name="all_documents_collection",
            embedding_function=self.embeddings,
            persist_directory=UNIFIED_INDEX_PATH
        )
        print(f"[Step 3] Initializing LLM...")
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, openai_api_key=OPENAI_API_KEY)
        print(f"[Step 4] Initializing Retriever...")
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        print(f"[Step 5] Initializing Prompt...")
        self.prompt = ChatPromptTemplate.from_template(
            """
            You are a helpful assistant that answers questions based on the context provided.
            
            Context:
            {context}
            
            Question: {input}
            
            Answer:
            """
        )
        print(f"[Step 6] Initializing Chain...")
        self.chain = create_retrieval_chain(
            self.retriever,
            create_stuff_documents_chain(self.llm, self.prompt)
        )
        print(f"[Step 7] QueryService Initialized Successfully!")

    async def answer_question(self, question: str):
        print(f"\n--- [START] New Query Received: '{question}' ---")
        result = await self.chain.ainvoke({"input": question})
        print("--- [END] Query Processing Complete ---\n")
        return result["answer"]