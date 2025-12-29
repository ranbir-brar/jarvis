"""
LLM Provider abstraction for Jarvis.
Supports Groq and Gemini with instructor for structured outputs.
"""

from typing import Optional, Any
import instructor

from app.config import config


def get_groq_client() -> Any:
    """Get an instructor-wrapped Groq client."""
    from groq import Groq
    
    client = Groq(api_key=config.GROQ_API_KEY)
    return instructor.from_groq(client, mode=instructor.Mode.JSON)


def get_gemini_client() -> Any:
    """Get an instructor-wrapped Gemini client."""
    import google.genai as genai
    
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    return instructor.from_genai(client, mode=instructor.Mode.JSON)


def get_llm_client() -> Any:
    """
    Get the appropriate LLM client based on configuration.
    
    Returns:
        Instructor-wrapped client for structured outputs
    """
    if config.MODEL_PROVIDER == "groq":
        return get_groq_client()
    elif config.MODEL_PROVIDER == "gemini":
        return get_gemini_client()
    else:
        raise ValueError(f"Unknown provider: {config.MODEL_PROVIDER}")


def get_model_name() -> str:
    """Get the model name based on current provider."""
    if config.MODEL_PROVIDER == "groq":
        return config.GROQ_MODEL
    elif config.MODEL_PROVIDER == "gemini":
        return config.GEMINI_MODEL
    else:
        raise ValueError(f"Unknown provider: {config.MODEL_PROVIDER}")


def get_vision_client() -> tuple[Any, str]:
    """
    Get a vision-capable client for screenshot-to-code.
    
    Returns:
        Tuple of (client, model_name)
    """
    # Gemini has vision capabilities
    if config.MODEL_PROVIDER == "gemini":
        return get_gemini_client(), config.GEMINI_MODEL
    
    # For Groq, we need to use a different approach
    # Groq doesn't have native vision, so we fall back to Gemini if available
    if config.GEMINI_API_KEY:
        return get_gemini_client(), config.GEMINI_MODEL
    
    raise ValueError("No vision-capable model available. Set GEMINI_API_KEY for screenshot-to-code.")


class LLMClient:
    """
    High-level LLM client wrapper.
    Provides a unified interface for text and vision tasks.
    """
    
    def __init__(self):
        self._client = None
        self._vision_client = None
        self._model = None
        self._vision_model = None
    
    @property
    def client(self) -> Any:
        """Lazy-load the main client."""
        if self._client is None:
            self._client = get_llm_client()
            self._model = get_model_name()
        return self._client
    
    @property
    def model(self) -> str:
        """Get the current model name."""
        if self._model is None:
            self._model = get_model_name()
        return self._model
    
    @property
    def vision_client(self) -> Any:
        """Lazy-load the vision client."""
        if self._vision_client is None:
            self._vision_client, self._vision_model = get_vision_client()
        return self._vision_client
    
    @property
    def vision_model(self) -> str:
        """Get the vision model name."""
        if self._vision_model is None:
            _, self._vision_model = get_vision_client()
        return self._vision_model
    
    def chat(self, messages: list, response_model: Any, **kwargs) -> Any:
        """
        Send a chat request with structured output.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            response_model: Pydantic model for response validation
            **kwargs: Additional arguments for the API call
            
        Returns:
            Validated response matching response_model
        """
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_model=response_model,
            **kwargs
        )
    
    def vision_chat(self, messages: list, response_model: Any, **kwargs) -> Any:
        """
        Send a vision chat request with structured output.
        
        Args:
            messages: List of message dicts, can include image content
            response_model: Pydantic model for response validation
            **kwargs: Additional arguments for the API call
            
        Returns:
            Validated response matching response_model
        """
        return self.vision_client.chat.completions.create(
            model=self.vision_model,
            messages=messages,
            response_model=response_model,
            **kwargs
        )


# Singleton instance
llm_client = LLMClient()
