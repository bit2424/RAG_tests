from src.databases.chroma_db import ChromaDBAdapter
from src.embeddings.embedding_models import EmbeddingModel
from src.retrievers.retriever import RAGRetriever

# Initialize components
db = ChromaDBAdapter("test_collection", "path/to/persist")
db.connect()

embedding_model = EmbeddingModel()
retriever = RAGRetriever(db, embedding_model)

# Add documents
documents = [
    "The quick brown fox jumps over the lazy dog",
    "Machine learning is a subset of artificial intelligence",
    "Python is a popular programming language"
]
retriever.add_documents(documents)

# Retrieve similar documents
results = retriever.retrieve("What is machine learning?", top_k=2)