"""
ChromaDB-based semantic memory for Jarvis.
Provides persistent vector storage for clipboard items and notes.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.config import config


class ChromaMemory:
    """
    Semantic memory store using ChromaDB.
    Provides save, search, and delete operations.
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the memory store.
        
        Args:
            persist_directory: Directory for persistent storage.
                             Defaults to config.MEMORY_DB_PATH.
        """
        self.persist_directory = persist_directory or config.MEMORY_DB_PATH
        self._client = None
        self._collection = None
    
    @property
    def client(self):
        """Lazy-load ChromaDB client."""
        if self._client is None:
            import chromadb
            
            # Ensure directory exists
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            
            self._client = chromadb.PersistentClient(path=self.persist_directory)
        return self._client
    
    @property
    def collection(self):
        """Get or create the memory collection."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name="jarvis_memory",
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection
    
    def add(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add content to memory.
        
        Args:
            content: Text content to store
            metadata: Optional metadata (label, category, etc.)
            
        Returns:
            ID of the stored document
        """
        doc_id = str(uuid.uuid4())
        
        # Build metadata
        doc_metadata = {
            "timestamp": datetime.now().isoformat(),
            "content_preview": content[:100] if len(content) > 100 else content
        }
        
        if metadata:
            doc_metadata.update({
                k: v for k, v in metadata.items() 
                if v is not None and isinstance(v, (str, int, float, bool))
            })
        
        self.collection.add(
            documents=[content],
            metadatas=[doc_metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def search(
        self,
        query: str,
        n_results: int = 5
    ) -> List[str]:
        """
        Search memory for matching content.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of matching content strings
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if results and results['documents']:
                return results['documents'][0]
            return []
            
        except Exception as e:
            print(f"Error searching memory: {e}")
            return []
    
    def search_with_metadata(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search memory and return results with metadata.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of dicts with 'content', 'metadata', 'id', 'distance'
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results or not results['documents'][0]:
                return []
            
            return [
                {
                    "content": doc,
                    "metadata": meta,
                    "id": doc_id,
                    "distance": dist
                }
                for doc, meta, doc_id, dist in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['ids'][0],
                    results['distances'][0]
                )
            ]
            
        except Exception as e:
            print(f"Error searching memory: {e}")
            return []
    
    def delete(self, doc_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"Error deleting from memory: {e}")
            return False
    
    def delete_by_content(self, content: str) -> bool:
        """
        Delete documents matching the content.
        
        Args:
            content: Content to search for and delete
            
        Returns:
            True if successful
        """
        try:
            # Search for matching documents
            results = self.search_with_metadata(content, n_results=10)
            
            # Delete exact matches
            for result in results:
                if result['content'] == content:
                    self.delete(result['id'])
            
            return True
        except Exception as e:
            print(f"Error deleting from memory: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all memory.
        
        Returns:
            True if successful
        """
        try:
            # Delete and recreate collection
            self.client.delete_collection("jarvis_memory")
            self._collection = None
            return True
        except Exception as e:
            print(f"Error clearing memory: {e}")
            return False
    
    def count(self) -> int:
        """
        Get the number of items in memory.
        
        Returns:
            Number of stored documents
        """
        try:
            return self.collection.count()
        except Exception:
            return 0
    
    def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all items in memory.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of all stored items with metadata
        """
        try:
            results = self.collection.get(
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            if not results or not results['documents']:
                return []
            
            return [
                {
                    "content": doc,
                    "metadata": meta,
                    "id": doc_id
                }
                for doc, meta, doc_id in zip(
                    results['documents'],
                    results['metadatas'],
                    results['ids']
                )
            ]
            
        except Exception as e:
            print(f"Error listing memory: {e}")
            return []


# Singleton instance (lazy-loaded)
_memory_instance: Optional[ChromaMemory] = None


def get_memory() -> Optional[ChromaMemory]:
    """
    Get the memory instance if enabled.
    
    Returns:
        ChromaMemory instance if enabled, None otherwise
    """
    global _memory_instance
    
    if not config.ENABLE_MEMORY:
        return None
    
    if _memory_instance is None:
        _memory_instance = ChromaMemory()
    
    return _memory_instance


if __name__ == "__main__":
    # Test memory
    memory = ChromaMemory(persist_directory="/tmp/jarvis_test_memory")
    
    # Add some items
    memory.add("My API key is sk-test-12345", {"label": "test_api_key", "category": "credential"})
    memory.add("SELECT * FROM users WHERE active = true", {"label": "active_users_query", "category": "code_snippet"})
    memory.add("Remember to deploy the new feature on Monday", {"category": "reminder"})
    
    # Search
    print("Searching for 'API':")
    results = memory.search("API key")
    for r in results:
        print(f"  - {r[:50]}...")
    
    print(f"\nTotal items: {memory.count()}")
    
    # Cleanup
    memory.clear()
    print("Memory cleared")
