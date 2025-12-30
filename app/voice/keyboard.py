"""
Keyboard listener for push-to-talk activation.
Supports both single keys and hotkey combinations.
"""

import threading
from typing import Callable, Optional, Set
from pynput import keyboard


class PushToTalk:
    """
    Push-to-talk activation using keyboard hotkey.
    Records audio while the hotkey is held.
    
    Default: Cmd+Shift+J
    """
    
    def __init__(
        self,
        on_activate: Optional[Callable[[], None]] = None,
        on_deactivate: Optional[Callable[[], None]] = None,
        hotkey: str = "cmd+shift+j"
    ):
        """
        Initialize push-to-talk.
        
        Args:
            on_activate: Callback when hotkey is pressed (start recording)
            on_deactivate: Callback when hotkey is released (stop recording)
            hotkey: Hotkey combination like "cmd+shift+j" or single key like "f5"
        """
        self.on_activate = on_activate
        self.on_deactivate = on_deactivate
        self.hotkey_str = hotkey.lower()
        self.is_active = False
        self.listener = None
        self._lock = threading.Lock()
        self._debug = True
        
        # Currently pressed keys
        self._pressed_keys: Set = set()
        
        # Parse the hotkey
        self._required_modifiers, self._trigger_key = self._parse_hotkey(hotkey)
        
        # Modifier key mappings
        self._modifier_map = {
            keyboard.Key.cmd: "cmd",
            keyboard.Key.cmd_l: "cmd",
            keyboard.Key.cmd_r: "cmd",
            keyboard.Key.ctrl: "ctrl",
            keyboard.Key.ctrl_l: "ctrl",
            keyboard.Key.ctrl_r: "ctrl",
            keyboard.Key.alt: "alt",
            keyboard.Key.alt_l: "alt",
            keyboard.Key.alt_r: "alt",
            keyboard.Key.shift: "shift",
            keyboard.Key.shift_l: "shift",
            keyboard.Key.shift_r: "shift",
        }
    
    def _parse_hotkey(self, hotkey: str):
        """
        Parse a hotkey string into modifiers and trigger key.
        
        Args:
            hotkey: String like "cmd+shift+j" or "f5"
            
        Returns:
            (set of modifier names, trigger key character or Key object)
        """
        parts = [p.strip().lower() for p in hotkey.split("+")]
        
        modifiers = set()
        trigger = None
        
        # Known modifiers
        modifier_names = {"cmd", "ctrl", "alt", "shift", "option"}
        
        # Function key map
        fkey_map = {f"f{i}": getattr(keyboard.Key, f"f{i}") for i in range(1, 13)}
        
        for part in parts:
            if part in modifier_names:
                if part == "option":
                    modifiers.add("alt")
                else:
                    modifiers.add(part)
            elif part in fkey_map:
                trigger = fkey_map[part]
            elif len(part) == 1:
                # Single character key
                trigger = part
            else:
                print(f"⚠️  Unknown key part: {part}")
        
        if trigger is None:
            print(f"⚠️  No trigger key found in hotkey '{hotkey}', defaulting to 'j'")
            trigger = "j"
        
        return modifiers, trigger
    
    def _get_current_modifiers(self) -> Set[str]:
        """Get the set of currently pressed modifier names."""
        modifiers = set()
        for key in self._pressed_keys:
            if key in self._modifier_map:
                modifiers.add(self._modifier_map[key])
        return modifiers
    
    def _check_hotkey_match(self, key) -> bool:
        """Check if the current key + modifiers match the hotkey."""
        # Check trigger key
        trigger_match = False
        
        if isinstance(self._trigger_key, keyboard.Key):
            trigger_match = (key == self._trigger_key)
        elif isinstance(key, keyboard.KeyCode) and key.char:
            trigger_match = (key.char.lower() == self._trigger_key)
        
        if not trigger_match:
            return False
        
        # Check modifiers
        current_mods = self._get_current_modifiers()
        return current_mods == self._required_modifiers
    
    def _on_press(self, key):
        """Handle key press."""
        self._pressed_keys.add(key)
        
        if self._debug and not self._is_modifier(key):
            mods = self._get_current_modifiers()
            key_str = self._key_to_string(key)
            if mods:
                print(f"[DEBUG] Pressed: {'+'.join(sorted(mods))}+{key_str}")
            else:
                print(f"[DEBUG] Pressed: {key_str}")
        
        try:
            if self._check_hotkey_match(key):
                with self._lock:
                    if not self.is_active:
                        self.is_active = True
                        if self._debug:
                            print(f"[DEBUG] ✓ Hotkey matched!")
                        if self.on_activate:
                            self.on_activate()
        except Exception as e:
            print(f"Key press error: {e}")
    
    def _on_release(self, key):
        """Handle key release."""
        self._pressed_keys.discard(key)
        
        # Deactivate when ANY part of the hotkey is released
        if self.is_active:
            # Check if trigger key was released
            trigger_released = False
            if isinstance(self._trigger_key, keyboard.Key):
                trigger_released = (key == self._trigger_key)
            elif isinstance(key, keyboard.KeyCode) and key.char:
                trigger_released = (key.char.lower() == self._trigger_key)
            
            # Or if a required modifier was released
            modifier_released = False
            if key in self._modifier_map:
                mod_name = self._modifier_map[key]
                if mod_name in self._required_modifiers:
                    modifier_released = True
            
            if trigger_released or modifier_released:
                with self._lock:
                    if self.is_active:
                        self.is_active = False
                        if self._debug:
                            print(f"[DEBUG] Hotkey released")
                        if self.on_deactivate:
                            self.on_deactivate()
    
    def _is_modifier(self, key) -> bool:
        """Check if key is a modifier."""
        return key in self._modifier_map
    
    def _key_to_string(self, key) -> str:
        """Convert a key to a readable string."""
        if isinstance(key, keyboard.KeyCode):
            return key.char if key.char else str(key)
        return str(key).replace("Key.", "")
    
    def start(self):
        """Start listening for keyboard events."""
        if self.listener is not None:
            return
        
        hotkey_display = self.hotkey_str.upper().replace("+", " + ")
        print(f"Push-to-talk: Hold [{hotkey_display}] to speak")
        
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
        """Check if hotkey is currently pressed."""
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
        hotkey="cmd+shift+j"
    )
    
    print("\n" + "=" * 50)
    print("Testing push-to-talk")
    print("Hold Cmd+Shift+J to test. Ctrl+C to exit.")
    print("=" * 50 + "\n")
    
    ptt.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        ptt.stop()
        print("\nDone")
