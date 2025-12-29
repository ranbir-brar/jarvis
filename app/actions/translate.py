"""
Translation action for Jarvis.
Translates text between languages.
"""

from typing import Optional

from app.llm.providers import llm_client
from app.llm.prompts import TRANSLATE_PROMPT
from app.llm.schemas import TranslateResponse


def translate_text(
    content: str,
    target_language: str = "english"
) -> Optional[str]:
    """
    Translate text to the target language.
    
    Args:
        content: Text to translate
        target_language: Target language for translation
        
    Returns:
        Translated text, or None on failure
    """
    try:
        prompt = TRANSLATE_PROMPT.format(
            target_language=target_language,
            content=content
        )
        
        messages = [
            {"role": "system", "content": "You are a professional translator. Output ONLY the translation with no explanations."},
            {"role": "user", "content": prompt}
        ]
        
        response = llm_client.chat(
            messages=messages,
            response_model=TranslateResponse
        )
        
        return response.translated_text
        
    except Exception as e:
        print(f"Error translating text: {e}")
        return None


def detect_language(content: str) -> Optional[str]:
    """
    Detect the language of the given text.
    
    Args:
        content: Text to analyze
        
    Returns:
        Detected language name, or None on failure
    """
    from pydantic import BaseModel, Field
    
    class LanguageDetection(BaseModel):
        language: str = Field(description="The detected language name in English")
        confidence: float = Field(description="Confidence score 0-1")
    
    try:
        messages = [
            {"role": "system", "content": "You are a language detection expert. Detect the language of the text."},
            {"role": "user", "content": f"What language is this text written in?\n\n{content[:500]}"}
        ]
        
        response = llm_client.chat(
            messages=messages,
            response_model=LanguageDetection
        )
        
        return response.language
        
    except Exception as e:
        print(f"Error detecting language: {e}")
        return None
