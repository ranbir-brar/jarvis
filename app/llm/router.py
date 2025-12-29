"""
Intent Router for Jarvis.
Routes user commands to appropriate actions via LLM.
"""

from typing import Optional, Union
from PIL import Image

from app.llm.schemas import AssistantResponse, ActionType
from app.llm.providers import llm_client
from app.llm.prompts import MAIN_SYSTEM_PROMPT


def get_clipboard_preview(content_type: str, content: Union[str, Image.Image, None]) -> str:
    """Generate a preview string for clipboard content."""
    if content_type == "empty" or content is None:
        return "[Clipboard is empty]"
    
    if content_type == "image":
        if isinstance(content, Image.Image):
            return f"[Image: {content.size[0]}x{content.size[1]} {content.mode}]"
        return "[Image in clipboard]"
    
    if content_type == "text":
        text = str(content)
        if len(text) > 500:
            return text[:500] + "..."
        return text
    
    return "[Unknown content type]"


def route_intent(
    command: str,
    clipboard_type: str,
    clipboard_content: Union[str, Image.Image, None],
    memory_context: Optional[str] = None
) -> AssistantResponse:
    """
    Route a user command to an action via LLM.
    
    Args:
        command: The user's voice command
        clipboard_type: Type of clipboard content ('text', 'image', 'empty')
        clipboard_content: The actual clipboard content
        memory_context: Optional context from memory search
        
    Returns:
        AssistantResponse with action type and parameters
    """
    # Build the system prompt with context
    clipboard_preview = get_clipboard_preview(clipboard_type, clipboard_content)
    
    system_prompt = MAIN_SYSTEM_PROMPT.format(
        clipboard_type=clipboard_type,
        clipboard_preview=clipboard_preview,
        command=command
    )
    
    # Add memory context if available
    if memory_context:
        system_prompt += f"\n\nMEMORY CONTEXT:\n{memory_context}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": command}
    ]
    
    # Get structured response from LLM
    response = llm_client.chat(
        messages=messages,
        response_model=AssistantResponse
    )
    
    # Validate response compatibility with clipboard type
    response = validate_action_compatibility(response, clipboard_type)
    
    return response


def validate_action_compatibility(
    response: AssistantResponse,
    clipboard_type: str
) -> AssistantResponse:
    """
    Validate that the action is compatible with the clipboard content.
    
    Returns corrected response if there's a mismatch.
    """
    # Actions that require image in clipboard
    image_required_actions = {
        ActionType.SCREENSHOT_TO_CODE,
        ActionType.REMOVE_BACKGROUND
    }
    
    # Actions that require text in clipboard
    text_required_actions = {
        ActionType.STRUCTURE_DATA,
        ActionType.DEBUG_CODE,
        ActionType.REWRITE_TEXT,
        ActionType.TRANSLATE,
        ActionType.CLIPBOARD_UTILITY
    }
    
    # Check image requirements
    if response.action_type in image_required_actions and clipboard_type != "image":
        return AssistantResponse(
            thinking="Action requires image but clipboard has text/empty",
            action_type=ActionType.SHORT_REPLY,
            message="Copy an image first",
            emoji="📋"
        )
    
    # Check text requirements
    if response.action_type in text_required_actions and clipboard_type != "text":
        return AssistantResponse(
            thinking="Action requires text but clipboard has image/empty",
            action_type=ActionType.SHORT_REPLY,
            message="Copy some text first",
            emoji="📋"
        )
    
    return response


def quick_classify(command: str) -> Optional[ActionType]:
    """
    Quick classification of obvious commands without LLM call.
    Returns None if LLM is needed for classification.
    """
    command_lower = command.lower()
    
    # Background removal
    if any(phrase in command_lower for phrase in ["remove background", "remove the background", "transparent"]):
        return ActionType.REMOVE_BACKGROUND
    
    # Screenshot to code
    if any(phrase in command_lower for phrase in ["code this", "make this react", "convert to react", "tailwind this", "make this html"]):
        return ActionType.SCREENSHOT_TO_CODE
    
    # Memory operations
    if any(phrase in command_lower for phrase in ["remember this", "save this", "store this"]):
        return ActionType.SAVE_TO_MEMORY
    
    if any(phrase in command_lower for phrase in ["where did i save", "find my", "search memory", "recall"]):
        return ActionType.SEARCH_MEMORY
    
    # For everything else, use LLM
    return None
