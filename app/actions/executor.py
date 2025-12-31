"""
Central action executor for Jarvis.
Dispatches actions based on the LLM response.
"""

from typing import Union, Tuple, Optional
from PIL import Image

from app.llm.schemas import AssistantResponse, ActionType
from app.clipboard import copy_text_to_clipboard, copy_image_to_clipboard
from app.notify import notify_success, notify_error, notify_info


def execute_action(
    response: AssistantResponse,
    clipboard_content: Union[str, Image.Image, None],
    clipboard_type: str,
    memory_client: Optional[any] = None
) -> Tuple[bool, str]:
    """
    Execute an action based on the LLM response.
    """
    action_type = response.action_type
    
    try:
        if action_type == ActionType.COPY_TEXT_TO_CLIPBOARD:
            return _handle_copy_text(response)
        
        elif action_type == ActionType.SHORT_REPLY:
            return _handle_short_reply(response)
        
        elif action_type == ActionType.NO_ACTION:
            return _handle_no_action(response)
        
        elif action_type == ActionType.SCREENSHOT_TO_CODE:
            return _handle_screenshot_to_code(response, clipboard_content)
        
        elif action_type == ActionType.STRUCTURE_DATA:
            return _handle_structure_data(response, clipboard_content)
        
        elif action_type == ActionType.DEBUG_CODE:
            return _handle_debug_code(response, clipboard_content)
        
        elif action_type == ActionType.REWRITE_TEXT:
            return _handle_rewrite_text(response, clipboard_content)
        
        elif action_type == ActionType.REMOVE_BACKGROUND:
            return _handle_remove_background(response, clipboard_content)
        
        elif action_type == ActionType.TRANSLATE:
            return _handle_translate(response, clipboard_content)
        
        elif action_type == ActionType.SAVE_TO_MEMORY:
            return _handle_save_to_memory(response, clipboard_content, memory_client)
        
        elif action_type == ActionType.SEARCH_MEMORY:
            return _handle_search_memory(response, memory_client)
        
        elif action_type == ActionType.DELETE_MEMORY:
            return _handle_delete_memory(response, memory_client)
        
        elif action_type == ActionType.CLEAR_MEMORY:
            return _handle_clear_memory(memory_client)
        
        elif action_type == ActionType.CLIPBOARD_UTILITY:
            return _handle_clipboard_utility(response, clipboard_content)
        
        else:
            notify_error(f"Unknown action: {action_type}")
            return False, f"Unknown action type: {action_type}"
            
    except Exception as e:
        error_msg = f"Error executing {action_type}: {str(e)}"
        notify_error(error_msg[:50])
        return False, error_msg


def _handle_copy_text(response: AssistantResponse) -> Tuple[bool, str]:
    """Handle COPY_TEXT_TO_CLIPBOARD action."""
    if not response.content:
        notify_error("No content to copy")
        return False, "No content provided"
    
    success = copy_text_to_clipboard(response.content)
    if success:
        notify_success(response.message)
        return True, response.message
    else:
        notify_error("Failed to copy")
        return False, "Failed to copy to clipboard"


def _handle_short_reply(response: AssistantResponse) -> Tuple[bool, str]:
    """Handle SHORT_REPLY action."""
    notify_info(response.message)
    return True, response.message


def _handle_no_action(response: AssistantResponse) -> Tuple[bool, str]:
    """Handle NO_ACTION."""
    if response.message:
        notify_info(response.message)
    return True, response.message or "No action needed"


def _handle_screenshot_to_code(
    response: AssistantResponse,
    clipboard_content: Union[str, Image.Image, None]
) -> Tuple[bool, str]:
    """Handle SCREENSHOT_TO_CODE action."""
    from app.actions.screenshot_to_code import screenshot_to_code
    
    if not isinstance(clipboard_content, Image.Image):
        notify_error("Need an image in clipboard")
        return False, "Clipboard does not contain an image"
    
    params = response.screenshot_to_code
    target = params.target if params else "react_tailwind"
    component_name = params.component_name if params else "Component"
    
    code = screenshot_to_code(clipboard_content, target, component_name)
    
    if code:
        success = copy_text_to_clipboard(code)
        if success:
            notify_success(response.message or "Code copied")
            return True, "Screenshot converted to code"
        else:
            notify_error("Failed to copy code")
            return False, "Failed to copy code to clipboard"
    else:
        notify_error("Failed to generate code")
        return False, "Failed to generate code from screenshot"


def _handle_structure_data(
    response: AssistantResponse,
    clipboard_content: Union[str, Image.Image, None]
) -> Tuple[bool, str]:
    """Handle STRUCTURE_DATA action."""
    from app.actions.structure_data import structure_data
    
    if not isinstance(clipboard_content, str):
        notify_error("Need text in clipboard")
        return False, "Clipboard does not contain text"
    
    params = response.data_structuring
    target_format = params.target_format if params else "json"
    sql_dialect = params.sql_dialect if params else "postgres"
    
    # If content is already provided by the router
    if response.content:
        result = response.content
    else:
        result = structure_data(clipboard_content, target_format, sql_dialect)
    
    if result:
        success = copy_text_to_clipboard(result)
        if success:
            # Show preview in notification (first 80 chars)
            preview = result[:80] + "..." if len(result) > 80 else result
            notify_success(f"{target_format.upper()}: {preview}")
            return True, f"Data structured as {target_format}"
        else:
            notify_error("Failed to copy")
            return False, "Failed to copy structured data"
    else:
        notify_error("Failed to structure data")
        return False, "Failed to structure data"


def _handle_debug_code(
    response: AssistantResponse,
    clipboard_content: Union[str, Image.Image, None]
) -> Tuple[bool, str]:
    """Handle DEBUG_CODE action."""
    from app.actions.debug_code import debug_code
    
    if not isinstance(clipboard_content, str):
        notify_error("Need code in clipboard")
        return False, "Clipboard does not contain text"
    
    params = response.debug_code
    mode = params.mode if params else "fix_only"
    
    if response.content:
        result = response.content
    else:
        result = debug_code(clipboard_content, mode)
    
    if result:
        success = copy_text_to_clipboard(result)
        if success:
            # Show short confirmation
            notify_success("Code fixed and copied!")
            return True, "Code debugged/fixed"
        else:
            notify_error("Failed to copy")
            return False, "Failed to copy fixed code"
    else:
        notify_error("Failed to debug code")
        return False, "Failed to debug code"


def _handle_rewrite_text(
    response: AssistantResponse,
    clipboard_content: Union[str, Image.Image, None]
) -> Tuple[bool, str]:
    """Handle REWRITE_TEXT action."""
    from app.actions.rewrite_text import rewrite_text
    
    if not isinstance(clipboard_content, str):
        notify_error("Need text in clipboard")
        return False, "Clipboard does not contain text"
    
    params = response.rewrite
    tone = params.tone if params else "professional"
    length = params.length if params else "same"
    
    if response.content:
        result = response.content
    else:
        result = rewrite_text(clipboard_content, tone, length)
    
    if result:
        success = copy_text_to_clipboard(result)
        if success:
            # Show preview in notification (first 80 chars)
            preview = result[:80] + "..." if len(result) > 80 else result
            notify_success(preview)
            return True, "Text rewritten"
        else:
            notify_error("Failed to copy")
            return False, "Failed to copy rewritten text"
    else:
        notify_error("Failed to rewrite text")
        return False, "Failed to rewrite text"


def _handle_remove_background(
    response: AssistantResponse,
    clipboard_content: Union[str, Image.Image, None]
) -> Tuple[bool, str]:
    """Handle REMOVE_BACKGROUND action."""
    from app.actions.bg_remove import remove_background
    
    if not isinstance(clipboard_content, Image.Image):
        notify_error("Need an image in clipboard")
        return False, "Clipboard does not contain an image"
    
    result = remove_background(clipboard_content)
    
    if result:
        success = copy_image_to_clipboard(result)
        if success:
            notify_success(response.message or "Background removed")
            return True, "Background removed"
        else:
            notify_error("Failed to copy image")
            return False, "Failed to copy image to clipboard"
    else:
        notify_error("Failed to remove background")
        return False, "Failed to remove background"


def _handle_translate(
    response: AssistantResponse,
    clipboard_content: Union[str, Image.Image, None]
) -> Tuple[bool, str]:
    """Handle TRANSLATE action."""
    from app.actions.translate import translate_text
    
    if not isinstance(clipboard_content, str):
        notify_error("Need text in clipboard")
        return False, "Clipboard does not contain text"
    
    params = response.translate
    target_language = params.target_language if params else "english"
    
    if response.content:
        result = response.content
    else:
        result = translate_text(clipboard_content, target_language)
    
    if result:
        success = copy_text_to_clipboard(result)
        if success:
            # Show preview in notification (first 80 chars)
            preview = result[:80] + "..." if len(result) > 80 else result
            notify_success(preview)
            return True, f"Translated to {target_language}"
        else:
            notify_error("Failed to copy")
            return False, "Failed to copy translation"
    else:
        notify_error("Failed to translate")
        return False, "Failed to translate text"


def _handle_save_to_memory(
    response: AssistantResponse,
    clipboard_content: Union[str, Image.Image, None],
    memory_client: Optional[any]
) -> Tuple[bool, str]:
    """Handle SAVE_TO_MEMORY action."""
    from app.actions.memory_store import save_to_memory
    
    if memory_client is None:
        notify_error("Memory not enabled")
        return False, "Memory feature is not enabled"
    
    content = str(clipboard_content) if clipboard_content else ""
    params = response.memory
    label = params.label if params else None
    category = params.category if params else "note"
    
    success = save_to_memory(memory_client, content, label, category)
    
    if success:
        notify_success(response.message or "Saved to memory")
        return True, "Saved to memory"
    else:
        notify_error("Failed to save")
        return False, "Failed to save to memory"


def _handle_search_memory(
    response: AssistantResponse,
    memory_client: Optional[any]
) -> Tuple[bool, str]:
    """Handle SEARCH_MEMORY action."""
    from app.actions.memory_store import search_memory
    
    if memory_client is None:
        notify_error("Memory not enabled")
        return False, "Memory feature is not enabled"
    
    # ALWAYS search the database - never trust LLM's response.content
    # The LLM might hallucinate values instead of retrieving real ones
    params = response.memory
    query = params.query if params else ""
    
    if not query:
        # Try to extract query from the original command
        query = response.message if response.message else ""
    
    results = search_memory(memory_client, query)
    
    if results:
        # Return the EXACT content from the database
        success = copy_text_to_clipboard(results[0])
        if success:
            notify_success(f"Found: {results[0][:30]}...")
            return True, "Memory result copied"
        else:
            notify_error("Failed to copy")
            return False, "Failed to copy memory result"
    else:
        notify_info("Nothing found in memory")
        return True, "No matching memory found"


def _handle_clipboard_utility(
    response: AssistantResponse,
    clipboard_content: Union[str, Image.Image, None]
) -> Tuple[bool, str]:
    """Handle CLIPBOARD_UTILITY action."""
    from app.actions.clipboard_utils import apply_utility
    
    if not isinstance(clipboard_content, str):
        notify_error("Need text in clipboard")
        return False, "Clipboard does not contain text"
    
    params = response.clipboard_utility
    operation = params.operation if params else "trim"
    
    result = apply_utility(clipboard_content, operation)
    
    if result is not None:
        success = copy_text_to_clipboard(result)
        if success:
            notify_success(response.message or f"Applied {operation}")
            return True, f"Applied {operation}"
        else:
            notify_error("Failed to copy")
            return False, "Failed to copy result"
    else:
        notify_error(f"Failed to apply {operation}")
        return False, f"Failed to apply {operation}"


def _handle_delete_memory(
    response: AssistantResponse,
    memory_client: Optional[any]
) -> Tuple[bool, str]:
    """Handle DELETE_MEMORY action."""
    if memory_client is None:
        notify_error("Memory not enabled")
        return False, "Memory feature is not enabled"
    
    # Get the query/label from the response
    params = response.memory
    query = params.query if params else None
    
    if not query:
        notify_error("Need query to find item to delete")
        return False, "No query provided for deletion"
    
    # Search for matching items
    results = memory_client.search_with_metadata(query, n_results=1)
    
    if results:
        # Delete the first match
        doc_id = results[0]['id']
        label = results[0].get('metadata', {}).get('label', 'item')
        success = memory_client.delete(doc_id)
        
        if success:
            notify_success(f"Deleted: {label}")
            return True, f"Deleted memory item: {label}"
        else:
            notify_error("Failed to delete")
            return False, "Failed to delete memory item"
    else:
        notify_info("No matching item found")
        return True, "No matching memory item found to delete"


def _handle_clear_memory(memory_client: Optional[any]) -> Tuple[bool, str]:
    """Handle CLEAR_MEMORY action."""
    if memory_client is None:
        notify_error("Memory not enabled")
        return False, "Memory feature is not enabled"
    
    success = memory_client.clear()
    
    if success:
        notify_success("Memory cleared!")
        return True, "All memory cleared"
    else:
        notify_error("Failed to clear memory")
        return False, "Failed to clear memory"
