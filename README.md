# Jarvis

> A macOS voice-activated clipboard assistant powered by AI.

Jarvis watches your clipboard and responds to voice commands to transform, analyze, and enhance whatever you've copied.

## Features

- **Push-to-Talk** — Hold `Cmd+Shift+J` to speak, release to process
- **Screenshot to Code** — Copy a UI screenshot, say "make this React"
- **Data Structuring** — Transform text to JSON, CSV, SQL, or Markdown
- **Code Debugging** — Copy buggy code, say "fix this"
- **Text Polishing** — Rewrite professionally, fix grammar
- **Background Removal** — Remove image backgrounds
- **Translation** — Translate between languages
- **Semantic Memory** — Save and recall information

## Quick Start

### Prerequisites

- macOS 13+
- Python 3.9+
- [Groq API key](https://console.groq.com) (free)

### Installation

```bash
git clone https://github.com/yourusername/jarvis.git
cd jarvis
pip install -r requirements.txt
brew install terminal-notifier
cp .env.example .env
```

### Configuration

Edit `.env` and add your Groq API key:

```bash
MODEL_PROVIDER=groq
GROQ_API_KEY=your_key_here
ACTIVATION_KEY=cmd+shift+j
```

### Running

```bash
python run.py
```

### macOS Permissions Required

1. **Microphone**: System Settings → Privacy & Security → Microphone
2. **Accessibility**: System Settings → Privacy & Security → Accessibility → Add Terminal

## Usage

**Hold `Cmd + Shift + J`** to speak, release to process. Result copied to clipboard.

| Command                | Action          |
| ---------------------- | --------------- |
| "make this JSON"       | Structure data  |
| "fix this"             | Debug code      |
| "make professional"    | Rewrite text    |
| "remove background"    | Remove image bg |
| "translate to Spanish" | Translate       |
| "stop"                 | Exit Jarvis     |

## Configuration

| Variable         | Default       | Description            |
| ---------------- | ------------- | ---------------------- |
| `MODEL_PROVIDER` | `groq`        | `groq` or `gemini`     |
| `GROQ_API_KEY`   | -             | Your API key           |
| `ACTIVATION_KEY` | `cmd+shift+j` | Hotkey to activate     |
| `ENABLE_MEMORY`  | `false`       | Enable semantic memory |

## Troubleshooting

**"No module named 'app'"** → Run with `python run.py`

**Hotkey not working** → Grant Accessibility permission to Terminal

**Microphone not working** → Grant Microphone permission

## License

MIT
