from sentence_transformers import SentenceTransformer
from typing import List, Union

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Generate embeddings for input texts."""
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts).tolist() 