# Jarvis

> A macOS voice-activated clipboard assistant powered by AI.

Jarvis watches your clipboard and responds to voice commands to transform, analyze, and enhance whatever you've copied — no tab switching, no context switching.

## Features

- **Screenshot to Code** — Copy a UI screenshot, say "Jarvis, make this React", get production-ready code
- **Data Structuring** — Transform messy text to JSON, CSV, SQL, or Markdown tables
- **Code Debugging** — Copy a stack trace or buggy code, say "Jarvis, fix this"
- **Text Polishing** — Rewrite text professionally, make it concise, fix grammar
- **Background Removal** — Remove backgrounds from images with one command
- **Translation** — Translate between languages automatically
- **Semantic Memory** — Save and recall information with natural language

## Quick Start

### Prerequisites

- macOS 13+ (Ventura or newer)
- Python 3.9+
- Homebrew (for terminal-notifier)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jarvis.git
cd jarvis

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install terminal-notifier for macOS notifications
brew install terminal-notifier

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` with your API keys:

```bash
# Choose provider: groq (recommended) or gemini
MODEL_PROVIDER=groq

# Add your API key
GROQ_API_KEY=your_key_here
# OR
GEMINI_API_KEY=your_key_here
```

### Running

```bash
cd jarvis
source venv/bin/activate
python app/main.py
```

## Voice Commands

| Action                   | Say                                                           |
| ------------------------ | ------------------------------------------------------------- |
| **Code from Screenshot** | "Jarvis, code this" / "make this React" / "Tailwind this"     |
| **Structure Data**       | "Jarvis, make this JSON" / "convert to CSV"                   |
| **Debug Code**           | "Jarvis, fix this" / "debug this"                             |
| **Rewrite Text**         | "Jarvis, make professional" / "simplify" / "fix grammar"      |
| **Background Removal**   | "Jarvis, remove background"                                   |
| **Translate**            | "Jarvis, translate" / "translate to Spanish"                  |
| **Memory**               | "Jarvis, remember this" / "where did I save...?"              |
| **Utilities**            | "Jarvis, trim whitespace" / "dedupe lines" / "extract emails" |
| **Stop**                 | "Jarvis, stop" / "goodbye"                                    |

## Architecture

```
jarvis/
├── app/
│   ├── main.py              # Main orchestrator
│   ├── clipboard.py         # macOS clipboard monitor
│   ├── notify.py            # macOS notifications
│   ├── config.py            # Configuration
│   ├── llm/                 # LLM layer
│   │   ├── schemas.py       # Pydantic models
│   │   ├── providers.py     # Groq/Gemini clients
│   │   ├── prompts.py       # System prompts
│   │   └── router.py        # Intent routing
│   ├── actions/             # Action handlers
│   │   ├── executor.py      # Central dispatch
│   │   ├── screenshot_to_code.py
│   │   ├── structure_data.py
│   │   ├── debug_code.py
│   │   ├── rewrite_text.py
│   │   ├── bg_remove.py
│   │   ├── translate.py
│   │   └── clipboard_utils.py
│   ├── voice/               # Voice pipeline
│   │   ├── transcribe.py    # Groq Whisper
│   │   ├── vad_stream.py    # Voice Activity Detection
│   │   └── wakeword.py      # Keyword detection
│   └── memory/              # Semantic memory
│       └── chroma_memory.py # ChromaDB store
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration Options

| Variable             | Default  | Description                      |
| -------------------- | -------- | -------------------------------- |
| `MODEL_PROVIDER`     | `groq`   | LLM provider: `groq` or `gemini` |
| `GROQ_API_KEY`       | -        | Groq API key                     |
| `GEMINI_API_KEY`     | -        | Gemini API key                   |
| `ENABLE_MEMORY`      | `false`  | Enable semantic memory           |
| `JARVIS_WAKEWORD`    | `jarvis` | Wakeword to activate             |
| `NOTIFICATION_TITLE` | `Jarvis` | macOS notification title         |

## Troubleshooting

### Microphone Permission

macOS will prompt for microphone access. Grant permission in:
**System Preferences → Privacy & Security → Microphone**

### terminal-notifier not found

```bash
brew install terminal-notifier
```

### Audio issues

Check your default input device:

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

## License

MIT
