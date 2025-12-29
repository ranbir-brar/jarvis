"""
Clipboard utility functions for Jarvis.
Simple text transformations that don't require LLM.
"""

import re
import json
from typing import Optional


def apply_utility(content: str, operation: str) -> Optional[str]:
    """
    Apply a clipboard utility operation.
    
    Args:
        content: Text content to transform
        operation: Operation to apply
        
    Returns:
        Transformed text, or None on failure
    """
    operations = {
        "trim": trim_whitespace,
        "dedupe_lines": dedupe_lines,
        "sort_lines": sort_lines,
        "extract_emails": extract_emails,
        "extract_urls": extract_urls,
        "prettify_json": prettify_json,
        "lowercase": lambda x: x.lower(),
        "uppercase": lambda x: x.upper(),
        "title_case": lambda x: x.title(),
        "reverse_lines": reverse_lines,
        "number_lines": number_lines,
        "remove_empty_lines": remove_empty_lines,
        "slugify": slugify,
        "url_encode": url_encode,
        "url_decode": url_decode,
    }
    
    op_func = operations.get(operation)
    if op_func:
        try:
            return op_func(content)
        except Exception as e:
            print(f"Error applying utility {operation}: {e}")
            return None
    else:
        print(f"Unknown utility operation: {operation}")
        return None


def trim_whitespace(content: str) -> str:
    """Trim leading/trailing whitespace from each line and overall."""
    lines = [line.strip() for line in content.split('\n')]
    return '\n'.join(lines).strip()


def dedupe_lines(content: str) -> str:
    """Remove duplicate lines while preserving order."""
    seen = set()
    result = []
    for line in content.split('\n'):
        if line not in seen:
            seen.add(line)
            result.append(line)
    return '\n'.join(result)


def sort_lines(content: str) -> str:
    """Sort lines alphabetically."""
    lines = content.split('\n')
    return '\n'.join(sorted(lines))


def reverse_lines(content: str) -> str:
    """Reverse the order of lines."""
    lines = content.split('\n')
    return '\n'.join(reversed(lines))


def number_lines(content: str) -> str:
    """Add line numbers."""
    lines = content.split('\n')
    width = len(str(len(lines)))
    return '\n'.join(f"{i+1:>{width}}. {line}" for i, line in enumerate(lines))


def remove_empty_lines(content: str) -> str:
    """Remove empty lines."""
    lines = [line for line in content.split('\n') if line.strip()]
    return '\n'.join(lines)


def extract_emails(content: str) -> str:
    """Extract email addresses."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, content)
    return '\n'.join(sorted(set(emails)))


def extract_urls(content: str) -> str:
    """Extract URLs."""
    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(pattern, content)
    return '\n'.join(sorted(set(urls)))


def prettify_json(content: str) -> str:
    """Prettify JSON with proper indentation."""
    data = json.loads(content)
    return json.dumps(data, indent=2)


def slugify(content: str) -> str:
    """Convert text to URL-friendly slug."""
    # Convert to lowercase
    slug = content.lower()
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Trim hyphens from ends
    return slug.strip('-')


def url_encode(content: str) -> str:
    """URL encode text."""
    from urllib.parse import quote
    return quote(content)


def url_decode(content: str) -> str:
    """URL decode text."""
    from urllib.parse import unquote
    return unquote(content)
