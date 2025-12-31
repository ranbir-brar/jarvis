#!/usr/bin/env python3
"""
Jarvis - macOS Voice Clipboard Assistant

Main entry point and orchestrator for the Jarvis voice assistant.
Uses push-to-talk: hold fn key to speak, release to process.
"""

import sys
import time
import signal
import threading
import io
import wave
from typing import Optional

import sounddevice as sd
import numpy as np

from app.config import config, Config
from app.clipboard import ClipboardMonitor, get_clipboard_content
from app.notify import notify_success, notify_error, notify_info
from app.voice.keyboard import PushToTalk
from app.voice.transcribe import transcribe_audio
from app.voice.wakeword import is_stop_command, normalize_command
from app.llm.router import route_intent
from app.actions.executor import execute_action
from app.memory.chroma_memory import get_memory


class Jarvis:
    """
    Main Jarvis application class.
    Uses push-to-talk: hold fn key to record, release to process.
    """
    
    def __init__(self, activation_key: str = "fn"):
        self.running = False
        self.clipboard_monitor = ClipboardMonitor()
        self.memory = get_memory()
        
        
        self.sample_rate = 16000
        self.channels = 1
        
        self.recording = False
        self.audio_frames = []
        self.audio_lock = threading.Lock()
        self.audio_stream = None
        
        self.processing = False
        
        self.ptt = PushToTalk(
            on_activate=self._start_recording,
            on_deactivate=self._stop_recording,
            hotkey=activation_key
        )
    
    def validate_config(self) -> bool:
        """Validate configuration before starting."""
        errors = Config.validate()
        if errors:
            for error in errors:
                print(f"Configuration error: {error}")
            return False
        return True
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream - stores frames while recording."""
        if status:
            print(f"Audio status: {status}")
        
        if self.recording:
            with self.audio_lock:
                # Store as int16
                audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
                self.audio_frames.append(audio_int16.tobytes())
    
    def _start_recording(self):
        """Called when activation key is pressed."""
        if self.processing:
            return
        
        with self.audio_lock:
            self.audio_frames = []
            self.recording = True
        
        print("\r🎤 Listening...            ", end="", flush=True)
    
    def _stop_recording(self):
        """Called when activation key is released."""
        if not self.recording:
            return
        
        with self.audio_lock:
            self.recording = False
            audio_data = b''.join(self.audio_frames)
            self.audio_frames = []
        
        print("\r⏹️  Processing...          ", end="", flush=True)
        print() # New line
        
        if len(audio_data) < 3200:  # Less than 0.1 seconds
            print("Recording too short, ignoring")
            return
        
        threading.Thread(
            target=self._process_audio,
            args=(audio_data,),
            daemon=True
        ).start()
    
    def _process_audio(self, audio_data: bytes):
        """Process recorded audio."""
        if self.processing:
            return
        
        self.processing = True
        
        try:
            wav_data = self._to_wav(audio_data)
            
            transcript = transcribe_audio(wav_data)
            if not transcript or not transcript.strip():
                print("No speech detected")
                notify_info("Didn't catch that")
                return
            
            print(f"📝 Heard: '{transcript}'")
            command = transcript.strip()
            
            if is_stop_command(command):
                notify_info("Goodbye!")
                self.stop()
                return
            
            command = normalize_command(command)
            
            clipboard_type, clipboard_content = get_clipboard_content()
            print(f"📋 Clipboard: {clipboard_type} ({len(str(clipboard_content)) if clipboard_content else 0} chars)")
            
            memory_context = None
            if self.memory:
                if any(word in command.lower() for word in ["find", "where", "search", "recall", "what was"]):
                    results = self.memory.search(command, n_results=3)
                    if results:
                        memory_context = "\n".join([f"- {r[:200]}" for r in results])
            
            print("🤖 Routing intent...")
            response = route_intent(
                command=command,
                clipboard_type=clipboard_type,
                clipboard_content=clipboard_content,
                memory_context=memory_context
            )
            print(f"🎯 Action: {response.action_type if response else 'None'}")
            
            print("⚡ Executing...")
            success, message = execute_action(
                response=response,
                clipboard_content=clipboard_content,
                clipboard_type=clipboard_type,
                memory_client=self.memory
            )
            
            if success:
                print(f"✅ Done: {message}")
            else:
                print(f"❌ Failed: {message}")
                
        except Exception as e:
            print(f"Error processing: {e}")
            import traceback
            traceback.print_exc()
            notify_error("Processing error")
        finally:
            self.processing = False

    def _to_wav(self, audio_data: bytes) -> bytes:
        """Convert raw PCM audio to WAV format."""
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(self.channels)
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(self.sample_rate)
            wav.writeframes(audio_data)
        return buffer.getvalue()
    
    def run(self):
        """Start Jarvis."""
        print("=" * 50)
        print("  Jarvis - Voice Clipboard Assistant")
        print("  Push-to-Talk Mode")
        print("=" * 50)
        
        if not self.validate_config():
            print("\nPlease fix configuration errors and try again.")
            sys.exit(1)
        
        print(f"\nProvider: {config.MODEL_PROVIDER}")
        print(f"Memory: {'Enabled' if config.ENABLE_MEMORY else 'Disabled'}")
        
        hotkey = config.ACTIVATION_KEY
        hotkey_display = hotkey.upper().replace("+", " + ")
        
        print(f"\n📌 Hold [{hotkey_display}] to speak, release to process")
        print("Say 'stop' to exit.\n")
        
        self.running = True
        
        notify_success(f"Ready! Hold {hotkey_display}")
        
        try:
            self.ptt.start()
            
            self.audio_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                callback=self._audio_callback
            )
            self.audio_stream.start()
            
            print("Ready and waiting...")
            
            while self.running:
                time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"Error: {e}")
            notify_error(f"Error: {str(e)[:30]}")
        finally:
            self.stop()

    def stop(self):
        """Stop Jarvis."""
        self.running = False
        self.recording = False
        
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None
        
        self.ptt.stop()
        print("\nJarvis stopped.")


def signal_handler(sig, frame):
    """Handle interrupt signals."""
    print("\nReceived interrupt signal")
    sys.exit(0)


def main():
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse activation key from args or config
    activation_key = config.ACTIVATION_KEY
    if len(sys.argv) > 1:
        activation_key = sys.argv[1]
    
    # Create and run Jarvis
    jarvis = Jarvis(activation_key=activation_key)
    jarvis.run()


if __name__ == "__main__":
    main()
