from setuptools import setup, find_packages

setup(
    name="src",
    version="0.1.0",
    description="A repository to test different RAG approaches",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "chromadb",
        "sentence-transformers",
        "pyyaml",
        "pytest",
        "qdrant-client",
        "datasets",
        "tqdm",
        "huggingface-hub",
        "sqlalchemy",  # Added for SQL schema handling
        "psycopg2-binary"  # Added for PostgreSQL support
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)