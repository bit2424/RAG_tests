from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VectorDatabase(ABC):
    """Base class for vector database implementations."""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the database."""
        pass
    
    @abstractmethod
    def insert(self, texts: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]] = None) -> None:
        """Insert documents and their embeddings into the database."""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using query embedding."""
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """Delete documents from the database."""
        pass 