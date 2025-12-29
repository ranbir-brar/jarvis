"""
macOS Clipboard Monitor using PyObjC/AppKit.
Provides functions to read and write text and images from the clipboard.
"""

import io
from typing import Tuple, Optional, Union
from PIL import Image

# macOS-specific imports
from AppKit import NSPasteboard, NSPasteboardTypePNG, NSPasteboardTypeString, NSPasteboardTypeTIFF
from Foundation import NSData


# Type alias for clipboard content
ClipboardContent = Tuple[str, Union[str, Image.Image, None]]


def get_clipboard_content() -> ClipboardContent:
    """
    Get the current clipboard content.
    
    Returns:
        Tuple of (content_type, content) where:
        - content_type is 'text', 'image', or 'empty'
        - content is str for text, PIL.Image for image, or None if empty
    """
    pasteboard = NSPasteboard.generalPasteboard()
    
    # Check for image first (PNG or TIFF)
    for image_type in [NSPasteboardTypePNG, NSPasteboardTypeTIFF]:
        image_data = pasteboard.dataForType_(image_type)
        if image_data:
            try:
                # Convert NSData to bytes and load as PIL Image
                data_bytes = bytes(image_data)
                image = Image.open(io.BytesIO(data_bytes))
                return ('image', image)
            except Exception:
                continue
    
    # Check for text
    text = pasteboard.stringForType_(NSPasteboardTypeString)
    if text:
        return ('text', str(text))
    
    return ('empty', None)


def copy_text_to_clipboard(text: str) -> bool:
    """
    Copy text to the clipboard.
    
    Args:
        text: The text to copy
        
    Returns:
        True if successful, False otherwise
    """
    try:
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        pasteboard.setString_forType_(text, NSPasteboardTypeString)
        return True
    except Exception as e:
        print(f"Error copying text to clipboard: {e}")
        return False


def copy_image_to_clipboard(image: Image.Image) -> bool:
    """
    Copy a PIL Image to the clipboard as PNG.
    
    Args:
        image: PIL Image to copy
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert PIL Image to PNG bytes
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        png_data = buffer.getvalue()
        
        # Create NSData from bytes
        ns_data = NSData.dataWithBytes_length_(png_data, len(png_data))
        
        # Set on pasteboard
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        pasteboard.setData_forType_(ns_data, NSPasteboardTypePNG)
        return True
    except Exception as e:
        print(f"Error copying image to clipboard: {e}")
        return False


def get_clipboard_change_count() -> int:
    """
    Get the clipboard change count.
    This increments each time the clipboard content changes.
    Useful for monitoring clipboard changes efficiently.
    
    Returns:
        Current change count
    """
    pasteboard = NSPasteboard.generalPasteboard()
    return pasteboard.changeCount()


class ClipboardMonitor:
    """
    Monitor clipboard for changes.
    """
    
    def __init__(self):
        self._last_change_count = get_clipboard_change_count()
        self._last_content: ClipboardContent = ('empty', None)
    
    def has_changed(self) -> bool:
        """Check if clipboard has changed since last check."""
        current_count = get_clipboard_change_count()
        if current_count != self._last_change_count:
            self._last_change_count = current_count
            return True
        return False
    
    def get_content(self, force_refresh: bool = False) -> ClipboardContent:
        """
        Get clipboard content, optionally forcing a refresh.
        
        Args:
            force_refresh: If True, always fetch from clipboard.
                          If False, return cached content if no change.
        """
        if force_refresh or self.has_changed():
            self._last_content = get_clipboard_content()
        return self._last_content


if __name__ == "__main__":
    # Simple test
    content_type, content = get_clipboard_content()
    print(f"Clipboard type: {content_type}")
    if content_type == 'text':
        print(f"Content: {content[:100]}..." if len(content) > 100 else f"Content: {content}")
    elif content_type == 'image':
        print(f"Image size: {content.size}")
