from databases.qdrant_db import QdrantAdapter
from databases.chroma_db import ChromaDBAdapter
from embeddings.embedding_models import EmbeddingModel
from retrievers.retriever import RAGRetriever
from utils.config import load_config

def main():
    # Load configuration
    config = load_config()
    
    # Initialize Qdrant
    qdrant_config = config['databases']['qdrant']
    qdrant_db = QdrantAdapter(
        collection_name=qdrant_config['collection_name'],
        vector_size=qdrant_config['vector_size'],
        host=qdrant_config['host'],
        port=qdrant_config['port']
    )
    qdrant_db.connect()
    
    # Initialize embedding model
    embedding_model = EmbeddingModel(model_name=config['embedding']['model_name'])
    
    # Initialize retriever
    retriever = RAGRetriever(qdrant_db, embedding_model)
    
    # Test the setup
    documents = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Python is a popular programming language"
    ]
    
    # Add documents
    retriever.add_documents(documents)
    
    # Test retrieval
    results = retriever.retrieve("What is machine learning?", top_k=2)
    
    print("Query: What is machine learning?")
    print("\nRetrieved documents:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Text: {result['text']}")
        print(f"   Distance: {result['distance']}")

if __name__ == "__main__":
    main() 