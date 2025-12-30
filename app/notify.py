"""
macOS Notifications using macos-notifications library.
Provides notification functionality with custom Jarvis icon.
"""

from typing import Optional
from pathlib import Path

from app.config import config

# Path to Jarvis logo for notifications
JARVIS_LOGO = Path(__file__).parent.parent / "public" / "jarvis_logo.png"


def notify(
    message: str,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    sound: bool = False
) -> bool:
    """
    Show a macOS notification with Jarvis icon.
    """
    try:
        from mac_notifications.client import create_notification
        
        create_notification(
            title=title or config.NOTIFICATION_TITLE,
            subtitle=subtitle or "",
            text=message,
            icon=str(JARVIS_LOGO) if JARVIS_LOGO.exists() else None
        )
        return True
    except ImportError:
        # Fallback to terminal-notifier
        return _notify_terminal_notifier(message, title, subtitle, sound)
    except Exception as e:
        print(f"Notification error: {e}")
        return _notify_terminal_notifier(message, title, subtitle, sound)


def _notify_terminal_notifier(
    message: str,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    sound: bool = False
) -> bool:
    """Fallback to terminal-notifier."""
    import subprocess
    import shutil
    
    if shutil.which("terminal-notifier") is None:
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
    notify_success("Jarvis is ready!", subtitle="Test notification")
