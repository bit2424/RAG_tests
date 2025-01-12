from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
from .base import VectorDatabase

class QdrantAdapter(VectorDatabase):
    def __init__(self, collection_name: str, vector_size: int = 384, host: str = "localhost", port: int = 6333):
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.host = host
        self.port = port
        self.client = None

    def connect(self) -> None:
        self.client = QdrantClient(host=self.host, port=self.port)
        
        # Create collection if it doesn't exist
        try:
            self.client.get_collection(self.collection_name)
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                )
            )

    def insert(self, texts: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]] = None) -> None:
        if metadata is None:
            metadata = [{} for _ in texts]

        # Add text to metadata for retrieval
        for i, text in enumerate(texts):
            metadata[i]["text"] = text

        points = [
            models.PointStruct(
                id=i,
                vector=embedding,
                payload=metadata[i]
            )
            for i, (embedding, meta) in enumerate(zip(embeddings, metadata))
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        
        return [
            {
                "text": hit.payload["text"],
                "metadata": {k: v for k, v in hit.payload.items() if k != "text"},
                "distance": hit.score
            }
            for hit in results
        ]

    def delete(self, ids: List[str]) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(
                points=ids
            )
        ) 