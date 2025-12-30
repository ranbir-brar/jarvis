"""
Screenshot to code action for Jarvis.
Converts UI screenshots to code using vision models.
"""

import io
from typing import Optional
from PIL import Image

from app.llm.prompts import SCREENSHOT_TO_CODE_PROMPT
from app.llm.schemas import VisionCodeResponse
from app.config import config


def image_to_bytes(image: Image.Image) -> bytes:
    """Convert PIL Image to PNG bytes."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


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
        import google.genai as genai
        from google.genai import types
        
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        image_bytes = image_to_bytes(image)
        
        prompt = SCREENSHOT_TO_CODE_PROMPT.format(
            target=target
        )
        
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/png',
                ),
                prompt
            ]
        )
        
        code = response.text
        
        if code.startswith("```"):
            lines = code.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)
        
        return code
        
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
