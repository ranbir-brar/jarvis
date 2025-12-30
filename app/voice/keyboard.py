"""
Keyboard listener for push-to-talk activation.
Uses pynput for global key detection.
"""

import threading
from typing import Callable, Optional
from pynput import keyboard


class PushToTalk:
    """
    Push-to-talk activation using keyboard.
    Records audio only while the activation key is held.
    
    Default: F5 key (function keys are most reliable)
    """
    
    def __init__(
        self,
        on_activate: Optional[Callable[[], None]] = None,
        on_deactivate: Optional[Callable[[], None]] = None,
        activation_key: str = "f5"
    ):
        """
        Initialize push-to-talk.
        
        Args:
            on_activate: Callback when key is pressed (start recording)
            on_deactivate: Callback when key is released (stop recording)
            activation_key: Key to use. Recommended: f5, f6, f7, f8
                           Also works: space, ctrl, alt, shift
        """
        self.on_activate = on_activate
        self.on_deactivate = on_deactivate
        self.activation_key = activation_key.lower()
        self.is_active = False
        self.listener = None
        self._lock = threading.Lock()
        self._debug = True  # Enable debug output
        
        # Map key names to pynput keys
        self._key_map = {
            # Function keys (MOST RELIABLE)
            "f1": keyboard.Key.f1,
            "f2": keyboard.Key.f2,
            "f3": keyboard.Key.f3,
            "f4": keyboard.Key.f4,
            "f5": keyboard.Key.f5,
            "f6": keyboard.Key.f6,
            "f7": keyboard.Key.f7,
            "f8": keyboard.Key.f8,
            "f9": keyboard.Key.f9,
            "f10": keyboard.Key.f10,
            "f11": keyboard.Key.f11,
            "f12": keyboard.Key.f12,
            # Modifier keys (less reliable when pressed alone)
            "ctrl": keyboard.Key.ctrl,
            "ctrl_l": keyboard.Key.ctrl_l,
            "ctrl_r": keyboard.Key.ctrl_r,
            "alt": keyboard.Key.alt,
            "alt_l": keyboard.Key.alt_l,
            "alt_r": keyboard.Key.alt_r,
            "cmd": keyboard.Key.cmd,
            "cmd_l": keyboard.Key.cmd_l,
            "cmd_r": keyboard.Key.cmd_r,
            "shift": keyboard.Key.shift,
            "shift_l": keyboard.Key.shift_l,
            "shift_r": keyboard.Key.shift_r,
            # Other keys
            "space": keyboard.Key.space,
            "tab": keyboard.Key.tab,
            "caps_lock": keyboard.Key.caps_lock,
        }
        
        self._target_key = self._get_activation_key()
    
    def _get_activation_key(self):
        """Get the pynput key object for the activation key."""
        key = self._key_map.get(self.activation_key)
        if key is None:
            print(f"⚠️  Unknown key '{self.activation_key}', defaulting to F5")
            return keyboard.Key.f5
        return key
    
    def _on_press(self, key):
        """Handle key press."""
        if self._debug:
            print(f"[DEBUG] Key pressed: {key}")
        
        try:
            if key == self._target_key:
                with self._lock:
                    if not self.is_active:
                        self.is_active = True
                        if self._debug:
                            print(f"[DEBUG] Activation key detected!")
                        if self.on_activate:
                            self.on_activate()
        except Exception as e:
            print(f"Key press error: {e}")
    
    def _on_release(self, key):
        """Handle key release."""
        if self._debug:
            print(f"[DEBUG] Key released: {key}")
        
        try:
            if key == self._target_key:
                with self._lock:
                    if self.is_active:
                        self.is_active = False
                        if self._debug:
                            print(f"[DEBUG] Activation key released!")
                        if self.on_deactivate:
                            self.on_deactivate()
        except Exception as e:
            print(f"Key release error: {e}")
    
    def start(self):
        """Start listening for keyboard events."""
        if self.listener is not None:
            return
        
        key_display = self.activation_key.upper()
        print(f"Push-to-talk: Hold [{key_display}] to speak")
        print(f"[DEBUG] Listening for key: {self._target_key}")
        
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
    
    def stop(self):
        """Stop listening for keyboard events."""
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def is_pressed(self) -> bool:
        """Check if activation key is currently pressed."""
        return self.is_active


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
        activation_key="f5"
    )
    
    print("\n" + "=" * 50)
    print("Testing push-to-talk")
    print("Press F5 to test. Ctrl+C to exit.")
    print("=" * 50 + "\n")
    
    ptt.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        ptt.stop()
        print("\nDone")
