# Jarvis — Complete Product Specification

> **Vision**: A macOS-native voice assistant that lives "in the flow" — it watches your clipboard, listens for a wakeword, and returns **actionable outputs** (code, structured data, polished text, transparent images) with **low latency** and zero UI friction.

---

## 1. Executive Summary

Jarvis eliminates workflow interruptions by operating directly on clipboard content. Copy something, speak a command, and receive the transformed result — no tab switching, no context switching, no copy-pasting into chat windows.

**Core Philosophy**: Keep users in their flow state by making AI assistance instantaneous and contextual.

**Primary Success Metric**: Median time from wakeword → clipboard updated ≤ **2 seconds** for text tasks.

---

## 2. Target Users & Use Cases

### Personas

| Persona            | Primary Use Case                         |
| ------------------ | ---------------------------------------- |
| **Frontend Dev**   | Screenshot UI → React/Tailwind code      |
| **Data Engineer**  | Messy text → clean CSV/JSON/SQL          |
| **Backend Dev**    | Stack trace → root cause + patched code  |
| **Writer/Student** | Draft text → polished, professional copy |
| **General User**   | Save snippets to memory, retrieve later  |

### Core Workflow

```
Copy something → Say "Jarvis [command]" → Clipboard updated + Notification shown
```

---

## 3. Tech Stack

### Core Technologies

| Component             | Technology                                                         |
| --------------------- | ------------------------------------------------------------------ |
| **Language**          | Python 3.9+                                                        |
| **macOS APIs**        | PyObjC / AppKit (NSPasteboard)                                     |
| **LLM Providers**     | Groq (`llama-3.3-70b-versatile`), Gemini (`gemini-2.5-flash-lite`) |
| **Structured Output** | Instructor + Pydantic                                              |
| **Voice**             | WebRTC VAD + Groq Whisper, or Picovoice Porcupine wakeword         |
| **Memory**            | ChromaDB (semantic vector search)                                  |
| **Notifications**     | terminal-notifier                                                  |
| **Image Processing**  | PIL/Pillow, rembg                                                  |

### Key Dependencies

```
groq
google-genai
instructor>=1.3.0
chromadb
pydantic>=2.0.0
sounddevice
webrtcvad
pyobjc (AppKit)
rembg
pillow
numpy
python-dotenv
```

---

## 4. Feature Set

### 4.1 Screenshot-to-Code

**Trigger**: Copy screenshot + "Jarvis, make this React/Tailwind/HTML"

**Output**: Clean, production-ready code copied to clipboard

**Constraints**:

- Semantic HTML (`<header>`, `<nav>`, `<button>`)
- Tailwind classes only (no inline CSS when Tailwind requested)
- Accessibility attributes (labels, button types)
- No explanations unless asked

---

### 4.2 Data Structuring

**Trigger**: Copy messy text + "Jarvis, make this JSON/CSV/SQL/Markdown table"

**Supported Formats**:

- **JSON**: Array of objects, consistent keys
- **CSV**: Valid quoting, consistent columns
- **SQL**: INSERT statements (default: Postgres)
- **Markdown Table**: Visual formatting

**Constraints**:

- Output validates (parseable JSON, consistent CSV)
- Never truncates data
- Infers schema automatically

---

### 4.3 Code Debugging & Refactoring

**Trigger**: Copy stack trace/code + "Jarvis, fix this" or "refactor this"

**Modes**:

- **Fix-only** (default): Returns corrected code only
- **Explain-only**: Short explanation (3-6 lines) when asked

**Constraints**:

- Preserves original intent
- Provides patch-style edits for incomplete code
- Never outputs essays by default

---

### 4.4 Text Polishing & Rewriting

**Trigger**: Copy text + "Jarvis, make this professional/concise/friendly"

**Tones**:

- **Professional**: Formal, structured, grammar-perfect
- **Concise**: 40-60% word reduction
- **Friendly**: Warm, conversational
- **Grammar Fix**: Corrections only, tone preserved

**Constraints**:

- Preserves all factual information
- No preambles like "Here's the rewritten version:"

---

### 4.5 Background Removal

**Trigger**: Copy image + "Jarvis, remove background"

**Output**: Transparent PNG copied to clipboard

**Implementation**: `rembg` library (works offline)

---

### 4.6 Semantic Memory

**Trigger**: "Jarvis, remember this as [label]" or "Jarvis, where did I save [query]"

**Operations**:

- **Save**: Store to ChromaDB with optional label
- **Search**: Semantic retrieval, best match copied to clipboard

**Categories**: `preference`, `important_info`, `note`, `code_snippet`

**Default**: Memory OFF for fast startup

---

### 4.7 Translation

**Trigger**: Copy text + "Jarvis, translate" or "translate to Spanish"

**Features**:

- Auto-detects source language
- Default target: English

---

### 4.8 Clipboard Utilities

**Triggers**:

- "Jarvis, trim whitespace"
- "Jarvis, dedupe lines"
- "Jarvis, sort lines"
- "Jarvis, extract emails/URLs"
- "Jarvis, prettify JSON"

---

### 4.9 Quick Calculations

**Trigger**: Copy value + "Jarvis, what's 15% of this?"

**Capabilities**:

- Percentage calculations
- Unit conversions (miles↔km, currency)
- Date math

---

## 5. System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────┐
│  1. CLIPBOARD MONITOR                               │
│     Polls NSPasteboard.changeCount()               │
│     Stores: ('text', str) or ('image', PIL.Image)  │
└──────────────────────┬──────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  2. VOICE PIPELINE                                  │
│     Wakeword detection (Porcupine or VAD+keyword)  │
│     Transcription (Groq Whisper)                   │
└──────────────────────┬──────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  3. INTENT ROUTER                                   │
│     Builds prompt: voice + clipboard + memory      │
│     LLM returns structured action JSON             │
└──────────────────────┬──────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  4. ACTION EXECUTOR                                 │
│     Dispatches to handler                          │
│     Updates clipboard                              │
│     Shows notification                             │
└─────────────────────────────────────────────────────┘
```

### Latency Budgets

| Stage                  | Target       |
| ---------------------- | ------------ |
| Wakeword detection     | < 200ms      |
| Transcription          | < 700–1200ms |
| LLM response           | < 800–1500ms |
| Clipboard + notify     | < 50ms       |
| **Total (text tasks)** | **< 2.5s**   |

---

## 6. Action Schema

All LLM responses follow this structured schema:

```json
{
  "thinking": "internal reasoning (not shown)",
  "actionType": "COPY_TEXT_TO_CLIPBOARD | SCREENSHOT_TO_CODE | STRUCTURE_DATA | DEBUG_CODE | REWRITE_TEXT | REMOVE_BACKGROUND | SAVE_TO_MEMORY | SEARCH_MEMORY | TRANSLATE | CALCULATE | SHORT_REPLY | NO_ACTION",
  "message": "≤50 chars for notification",
  "emoji": "happy|thinking|excited|...",
  "content_for_clipboard": "string output",
  "screenshot_to_code": {
    "target": "react_tailwind | html_css",
    "component_name": "ComponentName"
  },
  "data_structuring": {
    "target_format": "json | csv | sql | markdown_table",
    "sql_dialect": "postgres"
  },
  "debug": {
    "mode": "fix_only | explain_only",
    "language": "python | js | ts"
  },
  "rewrite": {
    "tone": "professional | concise | friendly",
    "length": "shorter | same"
  },
  "memory": {
    "operation": "save | search",
    "query": "string",
    "name": "optional label"
  }
}
```

**App-side Validation**:

- Validate enum values
- Check clipboard type compatibility (image required for screenshot-to-code)
- Fallback to `SHORT_REPLY` with helpful message on mismatch

---

## 7. Project Structure

```
jarvis/
├── app/
│   ├── main.py              # Main orchestrator
│   ├── clipboard.py         # macOS clipboard monitor
│   ├── notify.py            # macOS notifications
│   ├── config.py            # Environment/settings
│   │
│   ├── voice/
│   │   ├── porcupine_wakeword.py
│   │   ├── vad_stream.py
│   │   └── transcribe.py
│   │
│   ├── llm/
│   │   ├── providers.py     # Groq/Gemini clients
│   │   ├── router.py        # Intent routing
│   │   ├── prompts.py       # System prompts
│   │   └── schemas.py       # Pydantic models
│   │
│   ├── actions/
│   │   ├── executor.py      # Central dispatch
│   │   ├── screenshot_to_code.py
│   │   ├── structure_data.py
│   │   ├── debug_code.py
│   │   ├── rewrite_text.py
│   │   ├── bg_remove.py
│   │   ├── translate.py
│   │   └── memory_store.py
│   │
│   ├── memory/
│   │   └── chroma_memory.py
│   │
│   └── assets/
│       └── emojis/
│
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 8. Configuration

### Environment Variables

```bash
# LLM Provider (required)
MODEL_PROVIDER=groq              # or gemini
GROQ_API_KEY=...
GEMINI_API_KEY=...

# Features
ENABLE_MEMORY=false              # Default OFF for speed
ENABLE_SCREENSHOT_TO_CODE=true

# Voice
JARVIS_WAKEWORD=jarvis

# UI
NOTIFICATION_TITLE=Jarvis
```

### macOS Requirements

- macOS 13+ (Ventura recommended)
- Microphone permission (mandatory)
- `brew install terminal-notifier`

---

## 9. Voice Commands Reference

| Action                   | Example Commands                                        |
| ------------------------ | ------------------------------------------------------- |
| **Code from Screenshot** | "Jarvis, code this", "make this React", "Tailwind this" |
| **Structure Data**       | "make this JSON", "convert to CSV", "SQL inserts"       |
| **Debug Code**           | "fix this", "debug this", "explain the bug"             |
| **Refactor**             | "refactor this", "make it cleaner", "optimize this"     |
| **Rewrite Text**         | "make professional", "simplify", "fix grammar"          |
| **Background Removal**   | "remove background"                                     |
| **Memory Save**          | "remember this", "save as [label]"                      |
| **Memory Search**        | "where did I save [X]?", "find my [X]"                  |
| **Translate**            | "translate", "translate to French"                      |
| **Utilities**            | "trim whitespace", "dedupe lines", "extract emails"     |

---

## 10. Implementation Phases

### Phase 0: Skeleton

- [ ] ClipboardMonitor (text + image)
- [ ] Notifier wrapper
- [ ] Main run loop

### Phase 1: Voice

- [ ] Wakeword detection (Porcupine or VAD+keyword)
- [ ] Speech capture → transcription

### Phase 2: LLM + Text Actions

- [ ] Structured response model (Pydantic)
- [ ] COPY_TEXT_TO_CLIPBOARD, SHORT_REPLY, NO_ACTION
- [ ] Data structuring, Rewrite, Debug

### Phase 3: Image Actions

- [ ] Background removal (rembg)
- [ ] Screenshot-to-code (vision model)

### Phase 4: Memory

- [ ] ChromaDB integration
- [ ] Save/search flows

### Phase 5: Polish

- [ ] Error handling
- [ ] Clipboard utilities
- [ ] Performance optimization

---

## 11. Security & Privacy

- **API Keys**: Environment variables only, never logged
- **Clipboard**: Never sent without explicit voice command
- **Memory**: Local ChromaDB only, never leaves device
- **Sensitive Data**: Detect patterns (API keys, SSN) and warn before processing
- **Wipe Command**: "Jarvis, clear all memory"

---

## 12. Testing

### Unit Tests

- Clipboard encode/decode
- Pydantic schema validation
- Memory store/search
- Action handlers

### Integration Tests

- Simulated clipboard + command → end-to-end action
- Latency measurement

### Manual QA

- [ ] Copy text → "make professional" → verify rewrite
- [ ] Copy image → "remove background" → verify transparency
- [ ] Copy code with error → "fix this" → verify correction
- [ ] Copy messy data → "make JSON" → verify valid JSON

---

## 13. Roadmap

### v1.0 — MVP

- Voice activation + wakeword
- Screenshot-to-code
- Data structuring
- Code debugging
- Text rewriting
- Background removal
- Semantic memory

### v1.1 — Enhancements

- Clipboard history + search
- Translation
- Quick calculations
- More utilities (prettify, extract)

### v1.2 — Polish

- Global hotkeys (without voice)
- Settings UI
- Export/import memory

### v2.0 — Advanced

- MCP support (plugin ecosystem)
- Multi-step workflows
- Self-hosted LLM option (Ollama)

---

## 14. Non-Goals

To keep scope manageable for MVP:

- ❌ Not a full desktop chat client
- ❌ Not an IDE plugin
- ❌ Not a design system extractor
- ❌ Not cross-platform (macOS only for v1)
