"""
Wakeword detection for Jarvis.
Simple keyword-based detection from transcripts.
"""

import re
from typing import Tuple, Optional

from app.config import config


def detect_wakeword(transcript: str) -> Tuple[bool, Optional[str]]:
    """
    Detect wakeword in transcript and extract the command.
    
    Args:
        transcript: Transcribed speech text
        
    Returns:
        Tuple of (wakeword_detected: bool, command: str or None)
    """
    transcript_lower = transcript.lower().strip()
    wakeword = config.WAKEWORD.lower()
    
    # Check if transcript starts with or contains the wakeword
    # Pattern: "jarvis, <command>" or "hey jarvis, <command>" or just "jarvis <command>"
    patterns = [
        rf"^hey\s+{wakeword}[\s,]+(.+)$",
        rf"^{wakeword}[\s,]+(.+)$",
        rf"^ok\s+{wakeword}[\s,]+(.+)$",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, transcript_lower)
        if match:
            command = match.group(1).strip()
            return True, command
    
    # Check if just the wakeword was spoken (might be followed by more speech)
    if transcript_lower.startswith(wakeword):
        # Remove the wakeword and return the rest
        command = transcript_lower[len(wakeword):].strip()
        if command.startswith(","):
            command = command[1:].strip()
        if command:
            return True, command
    
    return False, None


def is_stop_command(command: str) -> bool:
    """
    Check if the command is a stop/exit command.
    
    Args:
        command: The command text
        
    Returns:
        True if it's a stop command
    """
    stop_phrases = [
        "stop",
        "exit",
        "quit",
        "goodbye",
        "bye",
        "shut down",
        "shutdown",
        "go away",
        "nevermind",
        "never mind",
        "cancel"
    ]
    
    command_lower = command.lower().strip()
    return command_lower in stop_phrases


def normalize_command(command: str) -> str:
    """
    Normalize a command for processing.
    Removes filler words and normalizes whitespace.
    
    Args:
        command: Raw command text
        
    Returns:
        Normalized command
    """
    # Remove common filler words at the start
    fillers = ["please", "can you", "could you", "would you", "uh", "um", "like"]
    
    command = command.strip()
    
    for filler in fillers:
        if command.lower().startswith(filler):
            command = command[len(filler):].strip()
            if command.startswith(","):
                command = command[1:].strip()
    
    # Normalize whitespace
    command = " ".join(command.split())
    
    return command
