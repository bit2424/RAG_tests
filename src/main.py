from src.databases.qdrant_db import QdrantAdapter
from src.databases.chroma_db import ChromaDBAdapter
from src.embeddings.embedding_models import EmbeddingModel
from src.retrievers.retriever import RAGRetriever
from src.utils.config import load_config
from src.utils.data_loader import HuggingFaceMetaLoader, DocumentProcessor
from typing import List, Dict, Any
import time
from contextlib import contextmanager

@contextmanager
def timer(description: str):
    """Utility context manager for timing code blocks."""
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{description}: {elapsed:.2f} seconds")

def explore_datasets(loader: HuggingFaceMetaLoader):
    """Explore and print dataset statistics."""
    stats = loader.get_dataset_stats()
    
    print("\n=== Dataset Statistics ===")
    print(f"Total Datasets: {stats['total_datasets']}")
    print(f"Unique Tasks: {stats['total_tasks']}")
    print(f"Unique Tags: {stats['total_tags']}")
    
    print("\n=== Popular Tasks ===")
    print(stats['popular_tasks'])
    
    print("\n=== Popular Tags ===")
    print(stats['popular_tags'])

def load_dataset_metadata(dataset_config: dict, max_documents: int = 10) -> List[Dict[str, Any]]:
    """Load and process dataset metadata from Hugging Face."""
    with timer("Initializing loaders"):
        loader = HuggingFaceMetaLoader()
        processor = DocumentProcessor()
    
    with timer("Searching/collecting dataset names"):
        if "datasets" in dataset_config:
            dataset_names = dataset_config["datasets"]
        elif "search" in dataset_config:
            search_config = dataset_config.get("search", {})
            dataset_names = loader.search_datasets(
                query=search_config.get("query"),
                task=search_config.get("task"),
                limit=search_config.get("limit", 5)
            )
        else:
            dataset_names = loader.metadata_dataset['datasetId'].tolist()
    
    print(f"\nProcessing {len(dataset_names)} datasets...")
    
    with timer("Processing dataset metadata"):
        all_documents = []
        for dataset_name in dataset_names:
            metadata = loader.load_dataset_metadata(dataset_name)
            if metadata:
                documents = processor.create_documents_from_metadata(metadata)
                all_documents.extend(documents)
                
            if max_documents and len(all_documents) >= max_documents:
                break
    
    print(f"Loaded {len(all_documents)} documents")
    return all_documents

def main():
    with timer("Loading configuration"):
        config = load_config()
    
    with timer("Initializing Qdrant"):
        qdrant_config = config['databases']['qdrant']
        qdrant_db = QdrantAdapter(
            collection_name=qdrant_config['collection_name'],
            vector_size=qdrant_config['vector_size'],
            host=qdrant_config['host'],
            port=qdrant_config['port']
        )
        qdrant_db.connect()
    
    with timer("Initializing embedding model"):
        embedding_model = EmbeddingModel(model_name=config['embedding']['model_name'])
    
    with timer("Initializing retriever"):
        retriever = RAGRetriever(qdrant_db, embedding_model)
    
    with timer("Loading dataset metadata"):
        dataset_documents = load_dataset_metadata(config['dataset'], max_documents=10)
        print(f"\nLoaded metadata for {len(dataset_documents)} documents")
    
    with timer("Adding documents to vector database"):
        texts = [doc["text"] for doc in dataset_documents]
        metadata = [doc["metadata"] for doc in dataset_documents]
        retriever.add_documents(texts, metadata=metadata)
    
    with timer("Performing test retrieval"):
        query = "What datasets are available for question answering?"
        results = retriever.retrieve(query, top_k=3)
        
        print(f"\nQuery: {query}")
        print("\nRetrieved documents:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}.")
            print(f"   Dataset: {result['metadata']['dataset']}")
            print(f"   Type: {result['metadata']['doc_type']}")
            print(f"   Tasks: {', '.join(result['metadata']['task_categories'])}")
            print(f"   Distance: {result['distance']}")

if __name__ == "__main__":
    with timer("Total execution"):
        main() 