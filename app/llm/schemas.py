"""
Pydantic schemas for Jarvis actions.
Defines the structured output format for LLM responses.
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """All supported action types."""
    
    # Text clipboard actions
    COPY_TEXT_TO_CLIPBOARD = "COPY_TEXT_TO_CLIPBOARD"
    SHORT_REPLY = "SHORT_REPLY"
    NO_ACTION = "NO_ACTION"
    
    # Feature actions
    SCREENSHOT_TO_CODE = "SCREENSHOT_TO_CODE"
    STRUCTURE_DATA = "STRUCTURE_DATA"
    DEBUG_CODE = "DEBUG_CODE"
    REWRITE_TEXT = "REWRITE_TEXT"
    REMOVE_BACKGROUND = "REMOVE_BACKGROUND"
    TRANSLATE = "TRANSLATE"
    
    # Memory actions
    SAVE_TO_MEMORY = "SAVE_TO_MEMORY"
    SEARCH_MEMORY = "SEARCH_MEMORY"
    DELETE_MEMORY = "DELETE_MEMORY"
    CLEAR_MEMORY = "CLEAR_MEMORY"
    
    # Utility actions
    CLIPBOARD_UTILITY = "CLIPBOARD_UTILITY"


class ScreenshotToCodeParams(BaseModel):
    """Parameters for screenshot-to-code action."""
    target: str = Field(
        default="react_tailwind",
        description="Target framework: react_tailwind, html_css, vue_tailwind"
    )
    component_name: str = Field(
        default="Component",
        description="Name for the generated component"
    )


class DataStructuringParams(BaseModel):
    """Parameters for data structuring action."""
    target_format: str = Field(
        description="Target format: json, csv, sql, markdown_table"
    )
    sql_dialect: str = Field(
        default="postgres",
        description="SQL dialect for SQL output: postgres, mysql, sqlite"
    )


class DebugCodeParams(BaseModel):
    """Parameters for code debugging action."""
    mode: str = Field(
        default="fix_only",
        description="Mode: fix_only, explain_only, fix_and_explain"
    )
    language: Optional[str] = Field(
        default=None,
        description="Detected programming language"
    )


class RewriteTextParams(BaseModel):
    """Parameters for text rewriting action."""
    tone: str = Field(
        default="professional",
        description="Tone: professional, concise, friendly, grammar_only"
    )
    length: str = Field(
        default="same",
        description="Length preference: shorter, same, longer"
    )


class TranslateParams(BaseModel):
    """Parameters for translation action."""
    source_language: Optional[str] = Field(
        default=None,
        description="Detected source language (auto if None)"
    )
    target_language: str = Field(
        default="english",
        description="Target language for translation"
    )


class MemoryParams(BaseModel):
    """Parameters for memory operations."""
    operation: str = Field(
        description="Operation: save, search"
    )
    query: Optional[str] = Field(
        default=None,
        description="Search query or content description"
    )
    label: Optional[str] = Field(
        default=None,
        description="Label/name for saved content"
    )
    category: str = Field(
        default="note",
        description="Category: preference, important_info, note, code_snippet"
    )


class ClipboardUtilityParams(BaseModel):
    """Parameters for clipboard utilities."""
    operation: str = Field(
        description="Operation: trim, dedupe_lines, sort_lines, extract_emails, extract_urls, prettify_json, lowercase, uppercase"
    )


class AssistantResponse(BaseModel):
    """
    Structured response from the LLM.
    This is the main schema that all LLM responses conform to.
    """
    
    thinking: str = Field(
        description="Internal reasoning (not shown to user)"
    )
    
    action_type: str = Field(
        description="The action to perform. Values: COPY_TEXT_TO_CLIPBOARD, SHORT_REPLY, NO_ACTION, SCREENSHOT_TO_CODE, STRUCTURE_DATA, DEBUG_CODE, REWRITE_TEXT, REMOVE_BACKGROUND, TRANSLATE, SAVE_TO_MEMORY, SEARCH_MEMORY, DELETE_MEMORY, CLEAR_MEMORY, CLIPBOARD_UTILITY"
    )
    
    message: str = Field(
        max_length=50,
        description="Short message for notification (max 50 chars)"
    )
    
    emoji: str = Field(
        default="✨",
        description="Emoji for the notification"
    )
    
    # Content for clipboard (used by most actions)
    content: Optional[str] = Field(
        default=None,
        description="Content to copy to clipboard"
    )
    
    # Action-specific parameters
    screenshot_to_code: Optional[ScreenshotToCodeParams] = Field(
        default=None
    )
    
    data_structuring: Optional[DataStructuringParams] = Field(
        default=None
    )
    
    debug_code: Optional[DebugCodeParams] = Field(
        default=None
    )
    
    rewrite: Optional[RewriteTextParams] = Field(
        default=None
    )
    
    translate: Optional[TranslateParams] = Field(
        default=None
    )
    
    memory: Optional[MemoryParams] = Field(
        default=None
    )
    
    clipboard_utility: Optional[ClipboardUtilityParams] = Field(
        default=None
    )


class VisionCodeResponse(BaseModel):
    """Response for screenshot-to-code vision model calls."""
    code: str = Field(description="Generated code")
    framework: str = Field(description="Framework used")
    notes: Optional[str] = Field(default=None, description="Implementation notes")


class StructuredDataResponse(BaseModel):
    """Response for data structuring."""
    structured_data: str = Field(description="The structured output")
    format: str = Field(description="Output format")
    columns: Optional[List[str]] = Field(default=None, description="Column names if tabular")


class DebugCodeResponse(BaseModel):
    """Response for code debugging."""
    fixed_code: str = Field(description="The corrected code")
    explanation: Optional[str] = Field(default=None, description="Brief explanation")
    language: str = Field(description="Programming language")


class RewriteResponse(BaseModel):
    """Response for text rewriting."""
    rewritten_text: str = Field(description="The rewritten text")
    tone: str = Field(description="Tone applied")


class TranslateResponse(BaseModel):
    """Response for translation."""
    translated_text: str = Field(description="The translated text")
    source_language: str = Field(description="Detected source language")
    target_language: str = Field(description="Target language")
