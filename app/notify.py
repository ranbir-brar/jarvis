"""
macOS Notifications using terminal-notifier.
Provides simple notification functionality for Jarvis.
"""

import subprocess
import shutil
from typing import Optional

from app.config import config


def is_terminal_notifier_available() -> bool:
    """Check if terminal-notifier is installed."""
    return shutil.which("terminal-notifier") is not None


def notify(
    message: str,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    sound: bool = False
) -> bool:
    """
    Show a macOS notification.
    
    Args:
        message: Main notification message
        title: Notification title (defaults to config.NOTIFICATION_TITLE)
        subtitle: Optional subtitle
        sound: Whether to play a sound
        
    Returns:
        True if notification was sent successfully, False otherwise
    """
    if not is_terminal_notifier_available():
        print(f"[Notification] {title or config.NOTIFICATION_TITLE}: {message}")
        return False
    
    try:
        cmd = [
            "terminal-notifier",
            "-title", title or config.NOTIFICATION_TITLE,
            "-message", message,
        ]
        
        if subtitle:
            cmd.extend(["-subtitle", subtitle])
        
        if sound:
            cmd.extend(["-sound", "default"])
        
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Notification error: {e}")
        return False
    except Exception as e:
        print(f"Notification error: {e}")
        return False


def notify_success(message: str, subtitle: Optional[str] = None) -> bool:
    """Show a success notification with ✅ prefix."""
    return notify(f"✅ {message}", subtitle=subtitle)


def notify_error(message: str, subtitle: Optional[str] = None) -> bool:
    """Show an error notification with ❌ prefix."""
    return notify(f"❌ {message}", subtitle=subtitle)


def notify_info(message: str, subtitle: Optional[str] = None) -> bool:
    """Show an info notification with ℹ️ prefix."""
    return notify(f"ℹ️ {message}", subtitle=subtitle)


if __name__ == "__main__":
    if is_terminal_notifier_available():
        notify_success("Jarvis is ready!", subtitle="Test notification")
    else:
        print("terminal-notifier not installed. Run: brew install terminal-notifier")
