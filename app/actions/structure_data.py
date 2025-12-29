"""
Data structuring action for Jarvis.
Converts text to JSON, CSV, SQL, or Markdown tables.
"""

from typing import Optional

from app.llm.providers import llm_client
from app.llm.prompts import STRUCTURE_DATA_PROMPT
from app.llm.schemas import StructuredDataResponse


def structure_data(
    content: str,
    target_format: str,
    sql_dialect: str = "postgres"
) -> Optional[str]:
    """
    Structure unstructured text into the target format.
    
    Args:
        content: The text content to structure
        target_format: Target format (json, csv, sql, markdown_table)
        sql_dialect: SQL dialect for SQL output
        
    Returns:
        Structured data as string, or None on failure
    """
    try:
        prompt = STRUCTURE_DATA_PROMPT.format(
            target_format=target_format,
            sql_dialect=sql_dialect,
            content=content
        )
        
        messages = [
            {"role": "system", "content": "You are a data structuring expert. Output ONLY the structured data with no explanations."},
            {"role": "user", "content": prompt}
        ]
        
        response = llm_client.chat(
            messages=messages,
            response_model=StructuredDataResponse
        )
        
        return response.structured_data
        
    except Exception as e:
        print(f"Error structuring data: {e}")
        return None


def quick_structure_json(content: str) -> Optional[str]:
    """
    Quick JSON structuring for simple cases.
    Attempts to parse and prettify existing JSON.
    """
    import json
    
    try:
        # Try to parse as JSON first
        data = json.loads(content)
        return json.dumps(data, indent=2)
    except json.JSONDecodeError:
        # Not valid JSON, need LLM
        return None


def quick_structure_csv_to_json(content: str) -> Optional[str]:
    """
    Quick conversion from CSV to JSON.
    """
    import csv
    import json
    from io import StringIO
    
    try:
        reader = csv.DictReader(StringIO(content))
        rows = list(reader)
        if rows:
            return json.dumps(rows, indent=2)
    except Exception:
        pass
    
    return None
