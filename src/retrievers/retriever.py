from typing import List, Dict, Any
from databases.base import VectorDatabase
from embeddings.embedding_models import EmbeddingModel

class RAGRetriever:
    def __init__(self, vector_db: VectorDatabase, embedding_model: EmbeddingModel):
        self.vector_db = vector_db
        self.embedding_model = embedding_model
    
    def add_documents(self, texts: List[str], metadata: List[Dict[str, Any]] = None) -> None:
        """Add documents to the vector database."""
        embeddings = self.embedding_model.encode(texts)
        self.vector_db.insert(texts, embeddings, metadata)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query."""
        query_embedding = self.embedding_model.encode(query)
        return self.vector_db.search(query_embedding[0], top_k=top_k) 