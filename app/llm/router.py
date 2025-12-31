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


def _build_quick_response(
    action_type: ActionType, 
    command: str, 
    clipboard_content: Union[str, Image.Image, None]
) -> AssistantResponse:
    """Build a response for quick-classified actions without LLM."""
    from app.llm.schemas import MemoryParams, DataStructuringParams
    import re
    
    # Extract label from command for memory operations
    label_match = re.search(r'(?:as my |as |my )(.+?)(?:\s*$|\.)', command.lower())
    label = label_match.group(1).strip() if label_match else None
    
    # Extract search query
    query_match = re.search(r"(?:what'?s my |what is my |find my |get my )(.+?)(?:\s*\?|$)", command.lower())
    query = query_match.group(1).strip() if query_match else command
    
    # Build response based on action type
    if action_type == ActionType.SAVE_TO_MEMORY:
        return AssistantResponse(
            thinking="Quick classify: save to memory",
            action_type=action_type.value,
            message=f"Saving as {label or 'note'}",
            emoji="💾",
            memory=MemoryParams(operation="save", label=label, category="important_info")
        )
    
    elif action_type == ActionType.SEARCH_MEMORY:
        return AssistantResponse(
            thinking="Quick classify: search memory",
            action_type=action_type.value,
            message=f"Searching for {query}",
            emoji="🔍",
            memory=MemoryParams(operation="search", query=query)
        )
    
    elif action_type == ActionType.DELETE_MEMORY:
        return AssistantResponse(
            thinking="Quick classify: delete memory",
            action_type=action_type.value,
            message=f"Deleting {query}",
            emoji="🗑️",
            memory=MemoryParams(operation="delete", query=query)
        )
    
    elif action_type == ActionType.CLEAR_MEMORY:
        return AssistantResponse(
            thinking="Quick classify: clear all memory",
            action_type=action_type.value,
            message="Clearing all memory",
            emoji="🧹",
            memory=MemoryParams(operation="clear")
        )
    
    elif action_type == ActionType.STRUCTURE_DATA:
        # Detect format from command
        fmt = "json" if "json" in command.lower() else "csv"
        return AssistantResponse(
            thinking="Quick classify: structure data",
            action_type=action_type.value,
            message=f"Converting to {fmt}",
            emoji="📊",
            structure_data=DataStructuringParams(target_format=fmt)
        )
    
    else:
        # Default for other quick actions
        return AssistantResponse(
            thinking="Quick classify: default action",
            action_type=action_type.value,
            message="Processing...",
            emoji="⚡"
        )


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
    # Try quick classification first (bypass LLM for common patterns)
    quick_action = quick_classify(command)
    if quick_action:
        # Build a minimal response for quick-classified actions
        return _build_quick_response(quick_action, command, clipboard_content)
    
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
    
    # Memory: Clear all
    if any(phrase in command_lower for phrase in ["clear all memory", "clear memory", "delete all memory", "erase memory", "wipe memory"]):
        return ActionType.CLEAR_MEMORY
    
    # Memory: Delete specific
    if any(phrase in command_lower for phrase in ["delete the", "forget my", "remove from memory", "delete my"]) and "memory" not in command_lower.split()[-2:]:
        return ActionType.DELETE_MEMORY
    
    # Memory: Save - must check BEFORE search
    if any(phrase in command_lower for phrase in ["remember this", "save this", "store this", "keep this", "save to memory"]):
        return ActionType.SAVE_TO_MEMORY
    
    # Memory: Search - expanded patterns
    if any(phrase in command_lower for phrase in [
        "what's my", "what is my", "whats my",
        "where did i save", "find my", "search memory", "recall",
        "get my", "show my", "retrieve my", "look up my"
    ]):
        return ActionType.SEARCH_MEMORY
    
    # Data structure
    if any(phrase in command_lower for phrase in ["convert to json", "convert to csv", "to json", "to csv", "make this json", "make this csv"]):
        return ActionType.STRUCTURE_DATA
    
    # Note: CALCULATE is NOT quick-classified because we need the LLM to compute the result
    
    # For everything else, use LLM
    return None
