"""
Configuration management for Jarvis.
Loads settings from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """Application configuration."""
    
    # LLM Provider Settings
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "groq")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Model names
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    GROQ_WHISPER_MODEL: str = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo")
    
    # Feature Flags
    ENABLE_MEMORY: bool = os.getenv("ENABLE_MEMORY", "false").lower() == "true"
    ENABLE_SCREENSHOT_TO_CODE: bool = os.getenv("ENABLE_SCREENSHOT_TO_CODE", "true").lower() == "true"
    
    # Voice Settings
    WAKEWORD: str = os.getenv("JARVIS_WAKEWORD", "jarvis")
    ACTIVATION_KEY: str = os.getenv("ACTIVATION_KEY", "cmd+shift+j")  # Hotkey like cmd+shift+j or single key like f5
    
    # UI Settings
    NOTIFICATION_TITLE: str = os.getenv("NOTIFICATION_TITLE", "Jarvis")
    
    # Memory Settings
    MEMORY_DB_PATH: str = os.getenv("MEMORY_DB_PATH", str(Path(__file__).parent / "memory" / "chroma_db"))
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration. Returns list of errors."""
        errors = []
        
        if cls.MODEL_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is required when MODEL_PROVIDER=groq")
        
        if cls.MODEL_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required when MODEL_PROVIDER=gemini")
        
        if cls.MODEL_PROVIDER not in ("groq", "gemini"):
            errors.append(f"MODEL_PROVIDER must be 'groq' or 'gemini', got '{cls.MODEL_PROVIDER}'")
        
        return errors


# Singleton instance
config = Config()
