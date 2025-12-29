"""
Background removal action for Jarvis.
Removes background from images using rembg.
"""

from typing import Optional
from PIL import Image


def remove_background(image: Image.Image) -> Optional[Image.Image]:
    """
    Remove background from an image.
    
    Args:
        image: PIL Image to process
        
    Returns:
        PIL Image with transparent background, or None on failure
    """
    try:
        from rembg import remove
        
        # Convert to RGBA if not already
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        # Remove background
        result = remove(image)
        
        return result
        
    except ImportError:
        print("rembg not installed. Install with: pip install rembg")
        return _fallback_remove_background(image)
    except Exception as e:
        print(f"Error removing background: {e}")
        return _fallback_remove_background(image)


def _fallback_remove_background(image: Image.Image) -> Optional[Image.Image]:
    """
    Fallback background removal using simple thresholding.
    This is a basic fallback when rembg is not available.
    
    Note: This only works well for images with solid color backgrounds.
    """
    try:
        # Convert to RGBA
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        # Get image data
        data = image.getdata()
        
        # Find the most common color (likely background)
        # This is a very simple heuristic
        from collections import Counter
        
        # Sample pixels from edges
        width, height = image.size
        edge_pixels = []
        
        for x in range(width):
            edge_pixels.append(image.getpixel((x, 0)))
            edge_pixels.append(image.getpixel((x, height - 1)))
        for y in range(height):
            edge_pixels.append(image.getpixel((0, y)))
            edge_pixels.append(image.getpixel((width - 1, y)))
        
        # Find most common edge color
        counter = Counter(edge_pixels)
        bg_color = counter.most_common(1)[0][0]
        
        # Create new image with transparency
        new_data = []
        tolerance = 30
        
        for item in data:
            # Check if pixel is close to background color
            if all(abs(item[i] - bg_color[i]) < tolerance for i in range(3)):
                new_data.append((255, 255, 255, 0))  # Transparent
            else:
                new_data.append(item)
        
        result = Image.new("RGBA", image.size)
        result.putdata(new_data)
        
        return result
        
    except Exception as e:
        print(f"Fallback background removal failed: {e}")
        return None


def is_rembg_available() -> bool:
    """Check if rembg is available."""
    try:
        import rembg
        return True
    except ImportError:
        return False
