#!/usr/bin/env python3
"""
Jarvis - macOS Voice Clipboard Assistant

Main entry point and orchestrator for the Jarvis voice assistant.
Monitors clipboard, listens for voice commands, and executes actions.
"""

import sys
import time
import signal
import threading
from typing import Optional

import sounddevice as sd
import numpy as np

from app.config import config, Config
from app.clipboard import ClipboardMonitor, get_clipboard_content
from app.notify import notify_success, notify_error, notify_info
from app.voice.vad_stream import VADStream, audio_bytes_to_wav
from app.voice.transcribe import transcribe_audio
from app.voice.wakeword import detect_wakeword, is_stop_command, normalize_command
from app.llm.router import route_intent
from app.actions.executor import execute_action
from app.memory.chroma_memory import get_memory


class Jarvis:
    """
    Main Jarvis application class.
    Orchestrates clipboard monitoring, voice processing, and action execution.
    """
    
    def __init__(self):
        self.running = False
        self.clipboard_monitor = ClipboardMonitor()
        self.memory = get_memory()
        
        # Voice settings
        self.sample_rate = 16000
        self.frame_duration_ms = 30
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
        
        # VAD
        self.vad = VADStream(
            sample_rate=self.sample_rate,
            frame_duration_ms=self.frame_duration_ms
        )
        
        # Audio buffer
        self.audio_buffer = b''
        self.audio_lock = threading.Lock()
        
        # Processing state
        self.processing = False
    
    def validate_config(self) -> bool:
        """Validate configuration before starting."""
        errors = Config.validate()
        if errors:
            for error in errors:
                print(f"Configuration error: {error}")
            return False
        return True
    
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream processing."""
        if status:
            print(f"Audio status: {status}")
        
        if self.processing:
            return
        
        # Convert float32 to int16
        audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
        
        with self.audio_lock:
            self.audio_buffer += audio_int16.tobytes()
            
            # Process complete frames
            frame_bytes = self.frame_size * 2  # 16-bit = 2 bytes per sample
            while len(self.audio_buffer) >= frame_bytes:
                frame = self.audio_buffer[:frame_bytes]
                self.audio_buffer = self.audio_buffer[frame_bytes:]
                
                speech_data = self.vad.process_frame(frame)
                if speech_data:
                    # Speech segment complete, process it
                    threading.Thread(
                        target=self.process_speech,
                        args=(speech_data,),
                        daemon=True
                    ).start()
    
    def process_speech(self, speech_data: bytes):
        """Process a detected speech segment."""
        if self.processing:
            return
        
        self.processing = True
        
        try:
            # Convert to WAV
            wav_data = audio_bytes_to_wav(speech_data, self.sample_rate)
            
            # Transcribe
            transcript = transcribe_audio(wav_data)
            if not transcript:
                return
            
            print(f"Heard: {transcript}")
            
            # Check for wakeword
            detected, command = detect_wakeword(transcript)
            if not detected:
                return
            
            print(f"Command: {command}")
            
            # Check for stop command
            if is_stop_command(command):
                notify_info("Goodbye!")
                self.stop()
                return
            
            # Normalize command
            command = normalize_command(command)
            
            # Get clipboard content
            clipboard_type, clipboard_content = get_clipboard_content()
            
            # Build memory context if enabled
            memory_context = None
            if self.memory:
                # Check if this might be a memory search
                if any(word in command.lower() for word in ["find", "where", "search", "recall", "what was"]):
                    results = self.memory.search(command, n_results=3)
                    if results:
                        memory_context = "\n".join([f"- {r[:200]}" for r in results])
            
            # Route intent via LLM
            response = route_intent(
                command=command,
                clipboard_type=clipboard_type,
                clipboard_content=clipboard_content,
                memory_context=memory_context
            )
            
            # Execute action
            success, message = execute_action(
                response=response,
                clipboard_content=clipboard_content,
                clipboard_type=clipboard_type,
                memory_client=self.memory
            )
            
            if not success:
                print(f"Action failed: {message}")
                
        except Exception as e:
            print(f"Error processing speech: {e}")
            notify_error("Processing error")
        finally:
            self.processing = False
    
    def run(self):
        """Start Jarvis."""
        print("=" * 50)
        print("  Jarvis - Voice Clipboard Assistant")
        print("=" * 50)
        
        # Validate config
        if not self.validate_config():
            print("\nPlease fix configuration errors and try again.")
            sys.exit(1)
        
        print(f"\nProvider: {config.MODEL_PROVIDER}")
        print(f"Memory: {'Enabled' if config.ENABLE_MEMORY else 'Disabled'}")
        print(f"Wakeword: '{config.WAKEWORD}'")
        print("\nSay 'Jarvis, <command>' to interact.")
        print("Say 'Jarvis, stop' to exit.\n")
        
        self.running = True
        
        # Show startup notification
        notify_success("Jarvis is ready!")
        
        try:
            # Start audio stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                blocksize=self.frame_size,
                callback=self.audio_callback
            ):
                print("Listening...")
                
                # Keep running until stopped
                while self.running:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"Error: {e}")
            notify_error("Audio error")
        finally:
            self.stop()
    
    def stop(self):
        """Stop Jarvis."""
        self.running = False
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
    
    # Create and run Jarvis
    jarvis = Jarvis()
    jarvis.run()


if __name__ == "__main__":
    main()
