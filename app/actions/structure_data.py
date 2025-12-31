"""
Data structuring action for Jarvis.
Converts text to JSON, CSV, SQL, or Markdown tables.
"""

import re
from typing import Optional

from app.config import config


def clean_markdown_table(content: str) -> str:
    """
    Clean markdown/HTML from table data before processing.
    Extracts visible text from markdown links and images.
    """
    # Remove markdown image/link combinations: [![alt](img)](url) -> alt
    content = re.sub(r'\[!\[([^\]]*)\]\([^)]*\)\]\([^)]*\)', r'\1', content)
    
    # Remove markdown images: ![alt](url) -> alt
    content = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', content)
    
    # Remove markdown links: [text](url) -> text
    content = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', content)
    
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Clean up <br> and whitespace
    content = re.sub(r'<br\s*/?>', ' ', content, flags=re.IGNORECASE)
    content = re.sub(r'\s+', ' ', content)
    
    # Clean table delimiters (multiple pipes, dashes)
    content = re.sub(r'\|\s*-+\s*', '|', content)
    content = re.sub(r'\|\s+\|', '|', content)
    
    return content.strip()


def get_raw_llm_response(messages: list) -> str:
    """
    Get raw text response from LLM without instructor schema overhead.
    This matches how Groq Playground works.
    """
    if config.MODEL_PROVIDER == "groq":
        from groq import Groq
        client = Groq(api_key=config.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=messages,
            temperature=0.1  # Low temp for accuracy
        )
        return response.choices[0].message.content
    
    elif config.MODEL_PROVIDER == "gemini":
        import google.genai as genai
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=messages[-1]["content"]  # User message
        )
        return response.text
    
    else:
        raise ValueError(f"Unsupported provider for raw output: {config.MODEL_PROVIDER}")


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
        # Clean markdown/HTML first
        cleaned_content = clean_markdown_table(content)
        
        # Truncate if too long (prevent token overflow)
        max_chars = 15000
        if len(cleaned_content) > max_chars:
            cleaned_content = cleaned_content[:max_chars] + "\n... (truncated)"
        
        # Simple, direct prompt - no schema overhead
        prompt = f"""Convert this data to {target_format} format.

RULES:
1. Output ONLY the {target_format} data - no explanations or markdown code blocks
2. Include ALL rows - never truncate
3. Copy values exactly as they appear

DATA:
{cleaned_content}"""
        
        messages = [
            {"role": "system", "content": "You are a data converter. Output only the converted data, nothing else."},
            {"role": "user", "content": prompt}
        ]
        
        # Get raw response without instructor overhead
        result = get_raw_llm_response(messages)
        
        # Clean up any markdown code block wrappers
        result = result.strip()
        if result.startswith("```"):
            lines = result.split("\n")
            result = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        
        return result.strip()
        
    except Exception as e:
        print(f"Error structuring data: {e}")
        return None


def csv_to_json(csv_content: str) -> str:
    """Convert CSV string to JSON string."""
    import csv
    import json
    from io import StringIO
    
    try:
        reader = csv.DictReader(StringIO(csv_content))
        rows = list(reader)
        return json.dumps(rows, indent=2)
    except Exception:
        return csv_content


def csv_to_sql(csv_content: str, dialect: str) -> str:
    """Convert CSV string to SQL INSERT statements."""
    import csv
    from io import StringIO
    
    try:
        reader = csv.reader(StringIO(csv_content))
        headers = next(reader)
        clean_headers = [h.strip().replace(" ", "_").lower() for h in headers]
        table_name = "data_table"
        
        statements = []
        # Create table
        cols = ", ".join([f"{h} TEXT" for h in clean_headers])
        statements.append(f"CREATE TABLE {table_name} ({cols});")
        
        # Inserts
        for row in reader:
            values = []
            for val in row:
                val = val.replace("'", "''") # Escape single quotes
                values.append(f"'{val}'")
            vals_str = ", ".join(values)
            statements.append(f"INSERT INTO {table_name} VALUES ({vals_str});")
            
        return "\n".join(statements)
    except Exception:
        return csv_content


def csv_to_markdown(csv_content: str) -> str:
    """Convert CSV string to Markdown table."""
    import csv
    from io import StringIO
    
    try:
        reader = csv.reader(StringIO(csv_content))
        headers = next(reader)
        
        lines = []
        # Header
        lines.append("| " + " | ".join(headers) + " |")
        # Separator
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        # Rows
        for row in reader:
            lines.append("| " + " | ".join(row) + " |")
            
        return "\n".join(lines)
    except Exception:
        return csv_content


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
