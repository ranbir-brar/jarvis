"""
macOS Notifications using terminal-notifier.
Provides robust notification functionality with sounds and Do-Not-Disturb bypass.
"""

import subprocess
import shutil
import os
from typing import Optional

from app.config import config


def is_terminal_notifier_available() -> bool:
    """Check if terminal-notifier is installed."""
    return shutil.which("terminal-notifier") is not None


def notify(
    message: str,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    sound: str = "Glass",
    group: Optional[str] = None,
    activate_url: Optional[str] = None
) -> bool:
    """
    Show a macOS notification with audio.
    Prioritizes terminal-notifier to bypass Do Not Disturb.
    Uses generic afplay for sound to ensure it's heard.
    """
    # 1. Play sound directly (works even if notifications are blocked)
    if sound:
        try:
            sound_file = f"/System/Library/Sounds/{sound}.aiff"
            if not os.path.exists(sound_file):
                sound_file = "/System/Library/Sounds/Glass.aiff"
            subprocess.Popen(["afplay", sound_file], stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # 2. Try terminal-notifier (bypasses Do Not Disturb)
    if is_terminal_notifier_available():
        try:
            cmd = ["terminal-notifier", "-message", message, "-ignoreDnD"]
            
            if title or config.NOTIFICATION_TITLE:
                cmd.extend(["-title", title or config.NOTIFICATION_TITLE])
            
            if subtitle:
                cmd.extend(["-subtitle", subtitle])
                
            if group:
                cmd.extend(["-group", group])
                
            if activate_url:
                cmd.extend(["-open", activate_url])
                
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"terminal-notifier failed: {e}")
            # Fall through to osascript

    # 3. Fallback to osascript (respects Do Not Disturb settings)
    try:
        title = title or config.NOTIFICATION_TITLE
        msg = message.replace('"', '\\"')
        ttl = title.replace('"', '\\"')
        
        script = f'display notification "{msg}" with title "{ttl}"'
        if subtitle:
            sub = subtitle.replace('"', '\\"')
            script += f' subtitle "{sub}"'
            
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Notification error: {e}")
        return False


def notify_success(message: str, subtitle: Optional[str] = None) -> bool:
    """Show a success notification with ✅ prefix."""
    return notify(f"✅ {message}", subtitle=subtitle, sound="Glass")


def notify_error(message: str, subtitle: Optional[str] = None) -> bool:
    """Show an error notification with ❌ prefix."""
    return notify(f"❌ {message}", subtitle=subtitle, sound="Basso")


def notify_info(message: str, subtitle: Optional[str] = None) -> bool:
    """Show an info notification with ℹ️ prefix."""
    return notify(f"ℹ️ {message}", subtitle=subtitle, sound="Tink")


if __name__ == "__main__":
    if is_terminal_notifier_available():
        notify_success("Jarvis is ready!", subtitle="Notifications configured")
    else:
        print("terminal-notifier not installed. Run: brew install terminal-notifier")
