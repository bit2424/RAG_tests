from databases.qdrant_db import QdrantAdapter
from embeddings.embedding_models import EmbeddingModel
from retrievers.retriever import RAGRetriever
from utils.config import load_config
from utils.sql_schema_loader import SQLSchemaLoader
from typing import List, Dict, Any
import time
from contextlib import contextmanager
import json

@contextmanager
def timer(description: str):
    """Utility context manager for timing code blocks."""
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{description}: {elapsed:.2f} seconds")

def load_sql_schemas(connection_string: str) -> List[Dict[str, Any]]:
    """Load and process SQL schema information."""
    with timer("Loading SQL schemas"):
        loader = SQLSchemaLoader(connection_string)
        schemas = loader.load_all_schemas()
    
    print(f"Loaded {len(schemas)} table schemas")
    return schemas

def analyze_json_structure(json_obj: Dict[str, Any], prefix: str = "") -> List[str]:
        """Analyze JSON structure and return field descriptions."""
        descriptions = []
        
        for key, value in json_obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                descriptions.extend(analyze_json_structure(value, full_key))
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                descriptions.append(f"{full_key}: Array of objects")
                descriptions.extend(analyze_json_structure(value[0], f"{full_key}[]"))
            else:
                type_name = type(value).__name__ if value is not None else "null"
                descriptions.append(f"{full_key}: {type_name}")
        
        return descriptions 
    
def analyze_json_query(json_obj: Dict[str, Any], loader: SQLSchemaLoader) -> str:
    """Analyze JSON structure and create a natural language query."""
    with timer("Analyzing JSON structure"):
        fields = analyze_json_structure(json_obj)
    
    query = "Find tables suitable for storing the following data structure:\n"
    query += "\n".join(fields)
    return query

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
    
    # Load SQL schemas
    connection_string = config['database']['connection_string']
    schema_loader = SQLSchemaLoader(connection_string)
    
    with timer("Loading SQL schemas"):
        schema_documents = load_sql_schemas(connection_string)
    
    with timer("Adding schemas to vector database"):
        texts = [doc["text"] for doc in schema_documents]
        metadata = [doc["metadata"] for doc in schema_documents]
        retriever.add_documents(texts, metadata=metadata)
    
    # Example JSON query
    sample_json = {
        "book": {
            "title": "The Great Gatsby",
            "isbn": "9780743273565",
            "author": {
                "first_name": "F. Scott",
                "last_name": "Fitzgerald"
            },
            "inventory": {
                "condition": "new",
                "quantity": 50,
                "retail_price": 15.99
            },
            "categories": ["Fiction", "Classics"]
        }
    }
    
    with timer("Performing schema matching"):
        query = analyze_json_query(sample_json, schema_loader)
        results = retriever.retrieve(query, top_k=5)
        
        print(f"\nAnalyzing JSON structure:\n{json.dumps(sample_json, indent=2)}")
        print(f"\nGenerated Query:\n{query}")
        print("\nRecommended tables:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Table: {result['metadata']['table_name']}")
            # print(f"   Schema:\n{json.dumps(result['metadata']['schema'], indent=2)}")
            # print(f"   Match Score: {1 - result['distance']:.2f}")

if __name__ == "__main__":
    with timer("Total execution"):
        main() 