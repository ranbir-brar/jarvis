"""
Voice Activity Detection using WebRTC VAD.
Detects when speech starts and ends in audio stream.
"""

import io
import wave
import collections
from typing import Optional, Callable, List

import numpy as np
import webrtcvad


class VADStream:
    """
    Voice Activity Detection stream processor.
    Detects speech segments in real-time audio.
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration_ms: int = 30,
        aggressiveness: int = 2,
        padding_duration_ms: int = 300,
        speech_threshold: float = 0.8
    ):
        """
        Initialize VAD stream.
        
        Args:
            sample_rate: Audio sample rate (must be 8000, 16000, 32000, or 48000)
            frame_duration_ms: Frame duration in ms (must be 10, 20, or 30)
            aggressiveness: VAD aggressiveness (0-3, higher = more aggressive filtering)
            padding_duration_ms: Padding to add before/after speech
            speech_threshold: Threshold for speech detection (0-1)
        """
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        self.padding_duration_ms = padding_duration_ms
        self.speech_threshold = speech_threshold
        
        # Number of frames for padding
        self.num_padding_frames = int(padding_duration_ms / frame_duration_ms)
        
        # Initialize VAD
        self.vad = webrtcvad.Vad(aggressiveness)
        
        # Ring buffer for padding
        self.ring_buffer = collections.deque(maxlen=self.num_padding_frames)
        
        # State
        self.triggered = False
        self.voiced_frames: List[bytes] = []
    
    def process_frame(self, frame: bytes) -> Optional[bytes]:
        """
        Process a single audio frame.
        
        Args:
            frame: Raw audio frame bytes (16-bit PCM)
            
        Returns:
            Complete speech segment if speech ended, None otherwise
        """
        is_speech = self.vad.is_speech(frame, self.sample_rate)
        
        if not self.triggered:
            self.ring_buffer.append((frame, is_speech))
            
            num_voiced = sum(1 for f, speech in self.ring_buffer if speech)
            
            if num_voiced > self.speech_threshold * self.ring_buffer.maxlen:
                self.triggered = True
                self.voiced_frames = [f for f, s in self.ring_buffer]
                self.ring_buffer.clear()
        else:
            self.voiced_frames.append(frame)
            self.ring_buffer.append((frame, is_speech))
            
            num_unvoiced = sum(1 for f, speech in self.ring_buffer if not speech)
            
            if num_unvoiced > self.speech_threshold * self.ring_buffer.maxlen:
                self.triggered = False
                speech_data = b''.join(self.voiced_frames)
                self.voiced_frames = []
                self.ring_buffer.clear()
                return speech_data
        
        return None
    
    def reset(self):
        """Reset the VAD state."""
        self.triggered = False
        self.voiced_frames = []
        self.ring_buffer.clear()


def audio_bytes_to_wav(audio_bytes: bytes, sample_rate: int = 16000) -> bytes:
    """
    Convert raw PCM audio bytes to WAV format.
    
    Args:
        audio_bytes: Raw 16-bit PCM audio
        sample_rate: Sample rate
        
    Returns:
        WAV file bytes
    """
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        wav.writeframes(audio_bytes)
    
    return buffer.getvalue()


def create_audio_stream(
    sample_rate: int = 16000,
    frame_duration_ms: int = 30,
    on_speech_end: Optional[Callable[[bytes], None]] = None
):
    """
    Create an audio stream with VAD processing.
    
    Args:
        sample_rate: Audio sample rate
        frame_duration_ms: Frame duration in ms
        on_speech_end: Callback when speech segment ends
        
    Returns:
        Tuple of (audio_callback, vad_stream)
    """
    import sounddevice as sd
    
    vad = VADStream(sample_rate=sample_rate, frame_duration_ms=frame_duration_ms)
    frame_size = int(sample_rate * frame_duration_ms / 1000)
    
    buffer = b''
    
    def audio_callback(indata, frames, time, status):
        nonlocal buffer
        
        if status:
            print(f"Audio status: {status}")
        
        # Convert float32 to int16
        audio_int16 = (indata * 32767).astype(np.int16)
        buffer += audio_int16.tobytes()
        
        # Process complete frames
        frame_bytes = frame_size * 2  # 16-bit = 2 bytes per sample
        while len(buffer) >= frame_bytes:
            frame = buffer[:frame_bytes]
            buffer = buffer[frame_bytes:]
            
            speech_data = vad.process_frame(frame)
            if speech_data and on_speech_end:
                wav_data = audio_bytes_to_wav(speech_data, sample_rate)
                on_speech_end(wav_data)
    
    return audio_callback, vad


def list_audio_devices():
    """List available audio input devices."""
    import sounddevice as sd
    
    devices = sd.query_devices()
    input_devices = []
    
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append({
                'id': i,
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': device['default_samplerate']
            })
    
    return input_devices
