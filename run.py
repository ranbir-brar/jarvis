#!/usr/bin/env python3
"""
Jarvis - macOS Voice Clipboard Assistant
Run this script to start Jarvis.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.main import main

if __name__ == "__main__":
    main()
