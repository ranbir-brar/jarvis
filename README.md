# Jarvis

> A macOS voice-activated clipboard assistant powered by AI.

Jarvis watches your clipboard and responds to voice commands to transform, analyze, and enhance whatever you've copied — no tab switching, no context switching.

## Features & Actions

Jarvis understands your intent and the content on your clipboard (text or image) to perform the following:

### Design & Code

- **Screenshot to Code**: Copy a UI screenshot → "Jarvis, make this React" → Generates production-ready code.
- **Debug Code**: Copy a stack trace or buggy code → "Jarvis, fix this" → Explains and fixes the bug.
- **Background Removal**: Copy an image → "Jarvis, remove background" → Updates clipboard with transparent PNG.

### Text & Data

- **Rewrite & Polish**: Copy rough notes → "Jarvis, make professional" → Rewrites text to be clear and polished.
- **Translate**: Copy text → "Jarvis, translate to Spanish" → Detects language and translates.
- **Structure Data**: Copy messy text → "Make this JSON" / "Convert to CSV" → Returns structured data.

### Memory

- **Semantic Memory**: "Jarvis, remember my API key is 123" → Saves to local database.
- **Recall**: "Jarvis, what is my API key?" → Searches memory and retrieves answer.
- **Delete**: "Jarvis, delete my API key from memory" → Removes specific item.
- **Clear**: "Jarvis, clear all memory" → Erases all stored data.

### Utilities

- **Quick Tools**: "Trim whitespace", "Dedupe lines", "Extract emails", "Extract URLs", "Prettify JSON", "Slugify".
- **Arithmetic**: "What's 15 \* 23?" → Calculates and copies result to clipboard.
- **Synonyms**: Copy a word → "What's a synonym for this?" → Copies synonyms to clipboard.

## Quick Start

### Prerequisites

- macOS 13+ (Ventura or newer)
- Python 3.9+
- [Groq API key](https://console.groq.com) (free)

### Installation

```bash
git clone https://github.com/yourusername/jarvis.git
cd jarvis

# Install dependencies
pip install -r requirements.txt
brew install terminal-notifier

# Configure
cp .env.example .env
```

### Configuration

Edit `.env` and add your Groq API key:

```bash
MODEL_PROVIDER=groq
GROQ_API_KEY=gsk_...
ACTIVATION_KEY=fn
```

### Running

```bash
python run.py
```

### Required Permissions

1. **Microphone**: System Settings → Privacy & Security → Microphone
2. **Accessibility**: System Settings → Privacy & Security → Accessibility → Add **Terminal** (required for `Fn` key detection)

## Usage

**Push-to-Talk**:

1. Hold the **`Fn`** key (Function key)
2. Speak your command
3. Release to process

| Context     | Copied Content        | Command (Example)        | Action                          |
| ----------- | --------------------- | ------------------------ | ------------------------------- |
| **Coding**  | Screenshot of a modal | "Code this in React"     | Generates React code            |
|             | Unformatted JSON      | "Prettify this"          | Formats JSON                    |
|             | Python error log      | "Fix this bug"           | Suggests code fix               |
| **Writing** | "meeting went good"   | "Make this professional" | "The meeting was productive..." |
|             | Paragraph of text     | "Translate to French"    | Returns French translation      |
| **Data**    | List of names/phones  | "Make CSV"               | Formats as CSV                  |
| **Memory**  | N/A                   | "Remember WiFi is 1234"  | Saves to memory                 |

## Configuration Options

| Variable                    | Default | Description                             |
| --------------------------- | ------- | --------------------------------------- |
| `MODEL_PROVIDER`            | `groq`  | `groq` or `gemini`                      |
| `GROQ_API_KEY`              | -       | Your API key                            |
| `ACTIVATION_KEY`            | `fn`    | Key to hold (`fn`, `cmd+shift+j`, etc.) |
| `ENABLE_MEMORY`             | `false` | Enable semantic memory                  |
| `ENABLE_SCREENSHOT_TO_CODE` | `true`  | Enable vision features                  |

## Troubleshooting

- **Notification doesn't appear**: Check System Settings → Notifications → `terminal-notifier`.
- **"Processing" but no result**: Check terminal output for errors.
- **Fn key not working**: Ensure Terminal has Accessibility permission and restart it.

## License

MIT
