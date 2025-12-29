"""
Keyboard listener for push-to-talk activation.
Detects when the fn key (or other activation key) is pressed.
"""

import threading
from typing import Callable, Optional
from pynput import keyboard


class PushToTalk:
    """
    Push-to-talk activation using keyboard.
    Records audio only while the activation key is held.
    """
    
    def __init__(
        self,
        on_activate: Optional[Callable[[], None]] = None,
        on_deactivate: Optional[Callable[[], None]] = None,
        activation_key: str = "fn"
    ):
        """
        Initialize push-to-talk.
        
        Args:
            on_activate: Callback when key is pressed (start recording)
            on_deactivate: Callback when key is released (stop recording)
            activation_key: Key to use for activation. Options:
                           "fn" - Function key
                           "ctrl" - Control key  
                           "alt" - Option key
                           "cmd" - Command key
                           "shift" - Shift key
                           "space" - Space bar
        """
        self.on_activate = on_activate
        self.on_deactivate = on_deactivate
        self.activation_key = activation_key
        self.is_active = False
        self.listener = None
        self._lock = threading.Lock()
        
        # Map key names to pynput keys
        self._key_map = {
            "fn": keyboard.Key.fn,
            "ctrl": keyboard.Key.ctrl,
            "alt": keyboard.Key.alt,
            "cmd": keyboard.Key.cmd,
            "shift": keyboard.Key.shift,
            "space": keyboard.Key.space,
            "f1": keyboard.Key.f1,
            "f2": keyboard.Key.f2,
            "f12": keyboard.Key.f12,
        }
    
    def _get_activation_key(self):
        """Get the pynput key object for the activation key."""
        return self._key_map.get(self.activation_key.lower(), keyboard.Key.fn)
    
    def _on_press(self, key):
        """Handle key press."""
        try:
            target_key = self._get_activation_key()
            
            if key == target_key:
                with self._lock:
                    if not self.is_active:
                        self.is_active = True
                        if self.on_activate:
                            self.on_activate()
        except Exception as e:
            print(f"Key press error: {e}")
    
    def _on_release(self, key):
        """Handle key release."""
        try:
            target_key = self._get_activation_key()
            
            if key == target_key:
                with self._lock:
                    if self.is_active:
                        self.is_active = False
                        if self.on_deactivate:
                            self.on_deactivate()
        except Exception as e:
            print(f"Key release error: {e}")
    
    def start(self):
        """Start listening for keyboard events."""
        if self.listener is not None:
            return
        
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        print(f"Push-to-talk: Hold [{self.activation_key}] to speak")
    
    def stop(self):
        """Stop listening for keyboard events."""
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def is_pressed(self) -> bool:
        """Check if activation key is currently pressed."""
        return self.is_active


class KeyboardShortcuts:
    """
    Handle keyboard shortcuts for Jarvis.
    """
    
    def __init__(self):
        self.listener = None
        self.shortcuts = {}
    
    def register(self, key_combo: str, callback: Callable[[], None]):
        """
        Register a keyboard shortcut.
        
        Args:
            key_combo: Key combination like "cmd+shift+j"
            callback: Function to call when shortcut is pressed
        """
        self.shortcuts[key_combo] = callback
    
    def _on_press(self, key):
        """Handle key press for shortcuts."""
        # TODO: Implement combo detection
        pass
    
    def start(self):
        """Start listening for shortcuts."""
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()
    
    def stop(self):
        """Stop listening for shortcuts."""
        if self.listener:
            self.listener.stop()
            self.listener = None


if __name__ == "__main__":
    # Test push-to-talk
    import time
    
    def on_start():
        print("🎤 Recording started...")
    
    def on_stop():
        print("⏹️  Recording stopped")
    
    ptt = PushToTalk(
        on_activate=on_start,
        on_deactivate=on_stop,
        activation_key="fn"
    )
    
    print("Testing push-to-talk. Press fn key to test. Ctrl+C to exit.")
    ptt.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        ptt.stop()
        print("\nDone")
