"""
Code debugging and refactoring action for Jarvis.
Fixes bugs, explains errors, and refactors code.
"""

from typing import Optional

from app.llm.providers import llm_client
from app.llm.prompts import DEBUG_CODE_PROMPT
from app.llm.schemas import DebugCodeResponse


def debug_code(
    content: str,
    mode: str = "fix_only"
) -> Optional[str]:
    """
    Debug or refactor code/error traces.
    
    Args:
        content: The code or error trace to debug
        mode: Debug mode (fix_only, explain_only, fix_and_explain)
        
    Returns:
        Fixed code or explanation, or None on failure
    """
    try:
        prompt = DEBUG_CODE_PROMPT.format(
            mode=mode,
            content=content
        )
        
        messages = [
            {"role": "system", "content": "You are a code debugging expert. Follow the mode instructions exactly."},
            {"role": "user", "content": prompt}
        ]
        
        response = llm_client.chat(
            messages=messages,
            response_model=DebugCodeResponse
        )
        
        if mode == "explain_only":
            return response.explanation or response.fixed_code
        elif mode == "fix_and_explain":
            result = response.fixed_code
            if response.explanation:
                result += f"\n\n// Explanation: {response.explanation}"
            return result
        else:
            return response.fixed_code
        
    except Exception as e:
        print(f"Error debugging code: {e}")
        return None


def fix_code(content: str) -> Optional[str]:
    """Fix code without explanation."""
    return debug_code(content, mode="fix_only")


def explain_error(content: str) -> Optional[str]:
    """Explain an error without fixing."""
    return debug_code(content, mode="explain_only")


def refactor_code(content: str) -> Optional[str]:
    """Refactor code for better readability/performance."""
    return debug_code(content, mode="fix_only")
