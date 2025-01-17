# RAG_tests
A respository to test different RAG approches.

```cmd
RAG_tests/
├── src/
│   ├── databases/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── chroma_db.py
│   │   ├── pinecone_db.py
│   │   └── milvus_db.py
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedding_models.py
│   ├── retrievers/
│   │   ├── __init__.py
│   │   └── retriever.py
│   └── utils/
│       ├── __init__.py
│       └── text_processing.py
├── tests/
│   ├── __init__.py
│   ├── test_databases/
│   ├── test_retrievers/
│   └── test_embeddings/
├── data/
│   ├── raw/
│   └── processed/
├── config/
│   └── config.yaml
├── requirements.txt
└── README.md 
```