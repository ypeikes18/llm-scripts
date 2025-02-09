import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from uuid import uuid4
load_dotenv()

#TODO: Clean this up and put it somewhere else
PATH = "./chroma_db"
MODEL = "text-embedding-ada-002"

def get_openai_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return key

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=PATH)        
        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=get_openai_key(),
            model_name=MODEL
        )
        
        # Initialize default collection
        self.default_collection = self.client.get_or_create_collection(
            name="default_collection",
            embedding_function=self.openai_ef,
            metadata={"description": "Default collection using OpenAI embeddings"}
        )

    def add_documents(self, documents, metadatas=None, ids=None, collection_name="default_collection"):
        """Add documents to the specified collection"""
        collection = self.client.get_collection(name=collection_name)
        
        if metadatas is None:
            metadatas = [{"source": "unknown"} for _ in documents]
        if ids is None:
            ids = [f"{uuid4()}" for i in range(len(documents))]
        
            
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search_similar(self, query_text, n_results=3, collection_name="default_collection"):
        """Search for similar documents in the specified collection"""
        collection = self.client.get_collection(name=collection_name)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

    def list_collections(self):
        """List all available collections"""
        return self.client.list_collections() 