import chromadb
from typing import List, Dict, Any
from src.databases.base import VectorDatabase

class ChromaDBAdapter(VectorDatabase):
    def __init__(self, collection_name: str, persist_directory: str = None):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
    
    def connect(self) -> None:
        self.client = chromadb.Client(
            chromadb.config.Settings(
                persist_directory=self.persist_directory
            ) if self.persist_directory else chromadb.config.Settings()
        )
        self.collection = self.client.get_or_create_collection(self.collection_name)
    
    def insert(self, texts: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]] = None) -> None:
        if metadata is None:
            metadata = [{} for _ in texts]
        
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadata,
            ids=[f"doc_{i}" for i in range(len(texts))]
        )
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return [
            {
                "text": doc,
                "metadata": metadata,
                "distance": distance
            }
            for doc, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    
    def delete(self, ids: List[str]) -> None:
        self.collection.delete(ids=ids) 