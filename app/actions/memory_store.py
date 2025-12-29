"""
Memory store actions for Jarvis.
Wrapper functions for memory operations.
"""

from typing import Optional, List, Any


def save_to_memory(
    memory_client: Any,
    content: str,
    label: Optional[str] = None,
    category: str = "note"
) -> bool:
    """
    Save content to memory.
    
    Args:
        memory_client: ChromaMemory instance
        content: Content to save
        label: Optional label/name for the content
        category: Category (preference, important_info, note, code_snippet)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        memory_client.add(
            content=content,
            metadata={
                "label": label,
                "category": category
            }
        )
        return True
    except Exception as e:
        print(f"Error saving to memory: {e}")
        return False


def search_memory(
    memory_client: Any,
    query: str,
    n_results: int = 5
) -> List[str]:
    """
    Search memory for matching content.
    
    Args:
        memory_client: ChromaMemory instance
        query: Search query
        n_results: Number of results to return
        
    Returns:
        List of matching content strings
    """
    try:
        results = memory_client.search(query, n_results=n_results)
        return results
    except Exception as e:
        print(f"Error searching memory: {e}")
        return []


def delete_memory(memory_client: Any, query: str) -> bool:
    """
    Delete matching items from memory.
    
    Args:
        memory_client: ChromaMemory instance
        query: Query to match items to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # First search for matching items
        results = memory_client.search(query, n_results=10)
        # Then delete them
        for result in results:
            memory_client.delete(result)
        return True
    except Exception as e:
        print(f"Error deleting from memory: {e}")
        return False


def clear_all_memory(memory_client: Any) -> bool:
    """
    Clear all memory.
    
    Args:
        memory_client: ChromaMemory instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        memory_client.clear()
        return True
    except Exception as e:
        print(f"Error clearing memory: {e}")
        return False
