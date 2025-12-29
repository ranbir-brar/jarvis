"""
Screenshot to code action for Jarvis.
Converts UI screenshots to code using vision models.
"""

import base64
import io
from typing import Optional
from PIL import Image

from app.llm.providers import llm_client
from app.llm.prompts import SCREENSHOT_TO_CODE_PROMPT
from app.llm.schemas import VisionCodeResponse


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def screenshot_to_code(
    image: Image.Image,
    target: str = "react_tailwind",
    component_name: str = "Component"
) -> Optional[str]:
    """
    Convert a screenshot to code using vision model.
    
    Args:
        image: PIL Image of the UI screenshot
        target: Target framework (react_tailwind, html_css, vue_tailwind)
        component_name: Name for the generated component
        
    Returns:
        Generated code string, or None on failure
    """
    try:
        # Convert image to base64
        image_b64 = image_to_base64(image)
        
        # Build the prompt
        prompt = SCREENSHOT_TO_CODE_PROMPT.format(
            target=target,
            component_name=component_name
        )
        
        # Build messages with image
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    }
                ]
            }
        ]
        
        # Use vision client
        response = llm_client.vision_chat(
            messages=messages,
            response_model=VisionCodeResponse
        )
        
        return response.code
        
    except Exception as e:
        print(f"Error in screenshot_to_code: {e}")
        return None


def get_framework_template(target: str, component_name: str) -> str:
    """Get a basic template for the target framework."""
    
    if target == "react_tailwind":
        return f'''export function {component_name}() {{
  return (
    <div className="p-4">
      {{/* Component content */}}
    </div>
  );
}}'''
    
    elif target == "html_css":
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{component_name}</title>
  <style>
    /* Styles */
  </style>
</head>
<body>
  <!-- Content -->
</body>
</html>'''
    
    elif target == "vue_tailwind":
        return f'''<script setup lang="ts">
// Component logic
</script>

<template>
  <div class="p-4">
    <!-- Component content -->
  </div>
</template>'''
    
    return ""
