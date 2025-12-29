"""
Text rewriting action for Jarvis.
Polishes, rewrites, or fixes grammar in text.
"""

from typing import Optional

from app.llm.providers import llm_client
from app.llm.prompts import REWRITE_TEXT_PROMPT
from app.llm.schemas import RewriteResponse


def rewrite_text(
    content: str,
    tone: str = "professional",
    length: str = "same"
) -> Optional[str]:
    """
    Rewrite text according to the specified tone and length.
    
    Args:
        content: The text to rewrite
        tone: Target tone (professional, concise, friendly, grammar_only)
        length: Length preference (shorter, same, longer)
        
    Returns:
        Rewritten text, or None on failure
    """
    try:
        prompt = REWRITE_TEXT_PROMPT.format(
            tone=tone,
            length=length,
            content=content
        )
        
        messages = [
            {"role": "system", "content": "You are a writing assistant. Output ONLY the rewritten text with no preamble."},
            {"role": "user", "content": prompt}
        ]
        
        response = llm_client.chat(
            messages=messages,
            response_model=RewriteResponse
        )
        
        return response.rewritten_text
        
    except Exception as e:
        print(f"Error rewriting text: {e}")
        return None


def fix_grammar(content: str) -> Optional[str]:
    """
    Quick grammar fix without changing tone or style.
    """
    return rewrite_text(content, tone="grammar_only", length="same")


def make_concise(content: str) -> Optional[str]:
    """
    Make text more concise (40-60% reduction).
    """
    return rewrite_text(content, tone="concise", length="shorter")


def make_professional(content: str) -> Optional[str]:
    """
    Make text more professional.
    """
    return rewrite_text(content, tone="professional", length="same")
