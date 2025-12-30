# Jarvis

> A macOS voice-activated clipboard assistant powered by AI.

Jarvis watches your clipboard and responds to voice commands to transform, analyze, and enhance whatever you've copied — no tab switching, no context switching.

## Features

- **Push-to-Talk** — Hold `fn` key to speak, release to process
- **Screenshot to Code** — Copy a UI screenshot, say "make this React", get production-ready code
- **Data Structuring** — Transform messy text to JSON, CSV, SQL, or Markdown tables
- **Code Debugging** — Copy a stack trace or buggy code, say "fix this"
- **Text Polishing** — Rewrite text professionally, make it concise, fix grammar
- **Background Removal** — Remove backgrounds from images with one command
- **Translation** — Translate between languages automatically
- **Semantic Memory** — Save and recall information with natural language

## Quick Start

### Prerequisites

- macOS 13+ (Ventura or newer)
- Python 3.9+
- [Groq API key](https://console.groq.com) (free)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jarvis.git
cd jarvis

# Install dependencies
pip install -r requirements.txt

# Install terminal-notifier for macOS notifications
brew install terminal-notifier

# Create your config file
cp .env.example .env
```

### Configuration

Edit `.env` and add your Groq API key:

```bash
MODEL_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
```

### Running Jarvis

```bash
python run.py
```

### macOS Permissions

On first run, you may need to grant permissions:

1. **Microphone**: System Settings → Privacy & Security → Microphone
2. **Accessibility** (for keyboard): System Settings → Privacy & Security → Accessibility

## Usage

**Push-to-Talk:**

1. Hold the `fn` key → 🎤 Recording starts
2. Speak your command
3. Release `fn` → ⏹️ Command is processed
4. Result is copied to clipboard + notification shown

### Voice Commands

| Action                   | Say                                                   |
| ------------------------ | ----------------------------------------------------- |
| **Code from Screenshot** | "code this" / "make this React" / "Tailwind this"     |
| **Structure Data**       | "make this JSON" / "convert to CSV"                   |
| **Debug Code**           | "fix this" / "debug this"                             |
| **Rewrite Text**         | "make professional" / "simplify" / "fix grammar"      |
| **Background Removal**   | "remove background"                                   |
| **Translate**            | "translate" / "translate to Spanish"                  |
| **Memory**               | "remember this" / "where did I save...?"              |
| **Utilities**            | "trim whitespace" / "dedupe lines" / "extract emails" |
| **Stop**                 | "stop" / "goodbye"                                    |

## Configuration Options

| Variable         | Default | Description                                                    |
| ---------------- | ------- | -------------------------------------------------------------- |
| `MODEL_PROVIDER` | `groq`  | LLM provider: `groq` or `gemini`                               |
| `GROQ_API_KEY`   | -       | Your Groq API key                                              |
| `GEMINI_API_KEY` | -       | Your Gemini API key (if using Gemini)                          |
| `ACTIVATION_KEY` | `fn`    | Push-to-talk key: `fn`, `ctrl`, `alt`, `cmd`, `shift`, `space` |
| `ENABLE_MEMORY`  | `false` | Enable semantic memory                                         |

## Project Structure

```
jarvis/
├── run.py               # Entry point - run this!
├── app/
│   ├── main.py          # Main orchestrator
│   ├── clipboard.py     # macOS clipboard monitor
│   ├── config.py        # Configuration
│   ├── notify.py        # macOS notifications
│   ├── llm/             # LLM layer (Groq/Gemini)
│   ├── actions/         # Action handlers
│   ├── voice/           # Voice pipeline + push-to-talk
│   └── memory/          # ChromaDB semantic memory
├── requirements.txt
├── .env.example
└── README.md
```

## Troubleshooting

### "No module named 'app'"

Make sure you run with `python run.py` from the jarvis directory.

### Microphone not working

Check System Settings → Privacy & Security → Microphone.

### Keyboard (fn key) not detected

Grant Accessibility permission to your terminal: System Settings → Privacy & Security → Accessibility.

### terminal-notifier not found

```bash
brew install terminal-notifier
```

## License

MIT
