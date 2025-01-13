from datasets import load_dataset
from typing import List, Dict, Any, Optional, Union
from tqdm import tqdm
import re
import pandas as pd

class HuggingFaceMetaLoader:
    """Loader for fetching dataset metadata from librarian-bots/dataset_cards_with_metadata."""
    
    def __init__(self):
        # Load dataset and convert to DataFrame
        self.metadata_dataset = pd.DataFrame(load_dataset("librarian-bots/dataset_cards_with_metadata")['train'])
        # Clean up DataFrame
        self.metadata_dataset = self._clean_dataframe()
    
    def _clean_dataframe(self) -> pd.DataFrame:
        """Clean and prepare the DataFrame."""
        df = self.metadata_dataset.copy()
        
        # Fill NaN values
        df['task_categories'] = df['task_categories'].fillna('').apply(lambda x: [] if x == '' else x)
        df['tags'] = df['tags'].fillna('').apply(lambda x: [] if x == '' else x)
        df['card'] = df['card'].fillna('')
        df['author'] = df['author'].fillna('')
        
        return df
    
    def load_dataset_metadata(self, dataset_name: str) -> Dict[str, Any]:
        """
        Load dataset metadata from the DataFrame.
        
        Args:
            dataset_name: Name of the dataset on Hugging Face
            
        Returns:
            Dictionary containing processed metadata and documentation
        """
        try:
            # Query the DataFrame
            dataset_info = self.metadata_dataset[self.metadata_dataset['datasetId'] == dataset_name]
            
            if dataset_info.empty:
                print(f"Dataset {dataset_name} not found in metadata collection")
                return {}
            
            # Get the first matching row
            row = dataset_info.iloc[0]
            
            metadata = {
                "name": dataset_name,
                "description": row['card'],
                "task_categories": row['task_categories'],
                "tags": row['tags'],
                "author": row['author'],
            }
            
            return metadata
            
        except Exception as e:
            print(f"Error loading metadata for {dataset_name}: {str(e)}")
            return {}

    def search_datasets(self, 
                       query: str = None, 
                       task: str = None,
                       limit: int = 100) -> List[str]:
        """
        Search for datasets based on various criteria using DataFrame operations.
        
        Args:
            query: Text search query
            task: Task category filter
            limit: Maximum number of results
            
        Returns:
            List of dataset names
        """
        # Start with all rows
        mask = pd.Series(True, index=self.metadata_dataset.index)
        
        # Apply filters
        if task:
            mask &= self.metadata_dataset['task_categories'].apply(lambda x: task in x)
        
        if query:
            mask &= self.metadata_dataset['card'].str.contains(query, case=False, na=False)
        
        # Get filtered results
        results = self.metadata_dataset[mask]['datasetId'].head(limit).tolist()
        return results

    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get general statistics about the datasets."""
        # Flatten task categories and tags for counting
        all_tasks = [task for tasks in self.metadata_dataset['task_categories'] for task in tasks if tasks]
        all_tags = [tag for tags in self.metadata_dataset['tags'] for tag in tags if tags]
        
        return {
            "total_datasets": len(self.metadata_dataset),
            "total_tasks": len(set(all_tasks)),
            "total_tags": len(set(all_tags)),
            "popular_tasks": pd.Series(all_tasks).value_counts().head(),
            "popular_tags": pd.Series(all_tags).value_counts().head()
        }

class DocumentProcessor:
    """Process and filter documents before insertion into vector database."""
    
    @staticmethod
    def create_documents_from_metadata(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert dataset metadata into documents for vector storage."""
        documents = []
        
        # Create document from basic metadata
        basic_info = (
            f"Dataset: {metadata['name']}\n"
            f"Description: {metadata['description']}\n"
            f"Tasks: {', '.join(metadata.get('task_categories', []))}\n"
            f"Tags: {', '.join(metadata.get('tags', []))}\n"
            f"Author: {metadata['author']}"
        )
        
        documents.append({
            "text": basic_info,
            "metadata": {
                "dataset": metadata["name"],
                "doc_type": "basic_info",
                "task_categories": metadata.get('task_categories', []),
                "tags": metadata.get('tags', [])
            }
        })
        
        return documents
    
    @staticmethod
    def filter_by_length(documents: List[Dict[str, Any]], 
                        min_length: int = 20, 
                        max_length: int = 2000) -> List[Dict[str, Any]]:
        """Filter documents by text length."""
        return [
            doc for doc in documents 
            if min_length <= len(doc["text"]) <= max_length
        ]
    
    @staticmethod
    def deduplicate(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate documents based on text content."""
        seen_texts = set()
        unique_docs = []
        
        for doc in documents:
            if doc["text"] not in seen_texts:
                seen_texts.add(doc["text"])
                unique_docs.append(doc)
        
        return unique_docs 