"""
Keyboard listener for push-to-talk activation.
Supports hotkey combinations and the special Fn key on macOS.
"""

import threading
from typing import Callable, Optional, Set
from pynput import keyboard

# Try to import Quartz for Fn key detection on macOS
try:
    import Quartz
    HAS_QUARTZ = True
except ImportError:
    HAS_QUARTZ = False


class FnKeyDetector:
    """
    Detects the Fn key on macOS using Quartz event tap.
    The Fn key is not visible to normal keyboard libraries.
    """
    
    def __init__(
        self,
        on_activate: Optional[Callable[[], None]] = None,
        on_deactivate: Optional[Callable[[], None]] = None
    ):
        self.on_activate = on_activate
        self.on_deactivate = on_deactivate
        self.is_active = False
        self._running = False
        self._thread = None
    
    def _event_callback(self, proxy, event_type, event, refcon):
        """Callback for Quartz event tap."""
        # Get current modifier flags
        flags = Quartz.CGEventGetFlags(event)
        
        # Check for Fn key (flag 0x800000 = 8388608)
        fn_pressed = bool(flags & 0x800000)
        
        if fn_pressed and not self.is_active:
            self.is_active = True
            if self.on_activate:
                self.on_activate()
        elif not fn_pressed and self.is_active:
            self.is_active = False
            if self.on_deactivate:
                self.on_deactivate()
        
        return event
    
    def _run_loop(self):
        """Run the event loop in a background thread."""
        # Create event tap for flagsChanged events (modifier keys)
        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionListenOnly,
            Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged),
            self._event_callback,
            None
        )
        
        if tap is None:
            print("⚠️  Failed to create event tap. Try granting Accessibility permission.")
            return
        
        # Create run loop source
        run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
        Quartz.CFRunLoopAddSource(
            Quartz.CFRunLoopGetCurrent(),
            run_loop_source,
            Quartz.kCFRunLoopCommonModes
        )
        
        # Enable the tap
        Quartz.CGEventTapEnable(tap, True)
        
        print("Push-to-talk: Hold [FN] to speak")
        
        # Run the loop
        while self._running:
            Quartz.CFRunLoopRunInMode(Quartz.kCFRunLoopDefaultMode, 0.1, False)
    
    def start(self):
        """Start listening for Fn key."""
        if not HAS_QUARTZ:
            print("⚠️  Quartz not available, Fn key detection won't work")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop listening."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)


class PushToTalk:
    """
    Push-to-talk activation using keyboard hotkey.
    Supports single keys, hotkey combinations, and the Fn key.
    
    Default: Cmd+Shift+J
    """
    
    def __init__(
        self,
        on_activate: Optional[Callable[[], None]] = None,
        on_deactivate: Optional[Callable[[], None]] = None,
        hotkey: str = "cmd+shift+j"
    ):
        self.on_activate = on_activate
        self.on_deactivate = on_deactivate
        self.hotkey_str = hotkey.lower()
        self.is_active = False
        self.listener = None
        self._lock = threading.Lock()
        self._debug = False
        
        # Check if using Fn key
        self._use_fn = (hotkey.lower() == "fn")
        
        if self._use_fn:
            self._fn_detector = FnKeyDetector(
                on_activate=on_activate,
                on_deactivate=on_deactivate
            )
        else:
            self._fn_detector = None
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
        """Parse a hotkey string into modifiers and trigger key."""
        parts = [p.strip().lower() for p in hotkey.split("+")]
        
        modifiers = set()
        trigger = None
        
        modifier_names = {"cmd", "ctrl", "alt", "shift", "option"}
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
                trigger = part
            else:
                print(f"⚠️  Unknown key: {part}")
        
        if trigger is None:
            trigger = "j"
        
        return modifiers, trigger
    
    def _get_current_modifiers(self) -> Set[str]:
        """Get set of currently pressed modifier names."""
        modifiers = set()
        for key in self._pressed_keys:
            if key in self._modifier_map:
                modifiers.add(self._modifier_map[key])
        return modifiers
    
    def _check_hotkey_match(self, key) -> bool:
        """Check if current key + modifiers match the hotkey."""
        trigger_match = False
        
        if isinstance(self._trigger_key, keyboard.Key):
            trigger_match = (key == self._trigger_key)
        elif isinstance(key, keyboard.KeyCode) and key.char:
            trigger_match = (key.char.lower() == self._trigger_key)
        
        if not trigger_match:
            return False
        
        current_mods = self._get_current_modifiers()
        return current_mods == self._required_modifiers
    
    def _on_press(self, key):
        """Handle key press."""
        self._pressed_keys.add(key)
        
        if self._debug:
            mods = self._get_current_modifiers()
            key_str = self._key_to_string(key)
            if mods:
                print(f"[DEBUG] Pressed: {'+'.join(sorted(mods))}+{key_str}")
        
        try:
            if self._check_hotkey_match(key):
                with self._lock:
                    if not self.is_active:
                        self.is_active = True
                        if self.on_activate:
                            self.on_activate()
        except Exception as e:
            print(f"Key press error: {e}")
    
    def _on_release(self, key):
        """Handle key release."""
        self._pressed_keys.discard(key)
        
        if self.is_active:
            trigger_released = False
            if isinstance(self._trigger_key, keyboard.Key):
                trigger_released = (key == self._trigger_key)
            elif isinstance(key, keyboard.KeyCode) and key.char:
                trigger_released = (key.char.lower() == self._trigger_key)
            
            modifier_released = False
            if key in self._modifier_map:
                mod_name = self._modifier_map[key]
                if mod_name in self._required_modifiers:
                    modifier_released = True
            
            if trigger_released or modifier_released:
                with self._lock:
                    if self.is_active:
                        self.is_active = False
                        if self.on_deactivate:
                            self.on_deactivate()
    
    def _key_to_string(self, key) -> str:
        """Convert a key to readable string."""
        if isinstance(key, keyboard.KeyCode):
            return key.char if key.char else str(key)
        return str(key).replace("Key.", "")
    
    def start(self):
        """Start listening for keyboard events."""
        if self._use_fn:
            self._fn_detector.start()
        else:
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
        """Stop listening."""
        if self._use_fn and self._fn_detector:
            self._fn_detector.stop()
        elif self.listener:
            self.listener.stop()
            self.listener = None


if __name__ == "__main__":
    import time
    
    def on_start():
        print("🎤 Recording...")
    
    def on_stop():
        print("⏹️  Stopped")
    
    # Test with Fn key
    ptt = PushToTalk(
        on_activate=on_start,
        on_deactivate=on_stop,
        hotkey="fn"
    )
    
    print("\n" + "=" * 50)
    print("Testing Fn key detection")
    print("Hold Fn to test. Ctrl+C to exit.")
    print("=" * 50 + "\n")
    
    ptt.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        ptt.stop()
        print("\nDone")
