"""
Transcription using Groq Whisper API.
"""

import io
from typing import Optional

from app.config import config


def transcribe_audio(audio_bytes: bytes) -> Optional[str]:
    """
    Transcribe audio bytes to text using Groq Whisper.
    
    Args:
        audio_bytes: Audio data in WAV format
        
    Returns:
        Transcribed text, or None on failure
    """
    try:
        from groq import Groq
        
        client = Groq(api_key=config.GROQ_API_KEY)
        
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        
        response = client.audio.transcriptions.create(
            model=config.GROQ_WHISPER_MODEL,
            file=audio_file,
            language="en"
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


def transcribe_audio_file(file_path: str) -> Optional[str]:
    """
    Transcribe an audio file to text.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Transcribed text, or None on failure
    """
    try:
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
        return transcribe_audio(audio_bytes)
    except Exception as e:
        print(f"Error reading audio file: {e}")
        return None
