# === Standard Library === 
import logging
from typing import Any

# === 3rd Party === 
from piper import PiperVoice

# backend/services/voice_service/tts_engine.py

from backend.event_bus import Events

class TTSEngine():
    def __init__(self, voice, synthesis_config):
        self.voice = voice
        self.synthesis_config = synthesis_config
    
    def speak(self, text: str) -> None:
        print(f"DEBUG: Piper starting synthesis for: '{text[:30]}...'")
        
        try:
            # Your original, correct implementation for the pip package
            chunks = self.voice.synthesize(text, syn_config=self.synthesis_config)
            
            chunk_count = 0
            for chunk in chunks:
                chunk_count += 1
                if chunk_count == 1:
                    print(f"DEBUG: First chunk generated! Size: {len(chunk.audio_int16_bytes)} bytes")
                
                # Emit the raw bytes directly
                Events.audio_out.emit(chunk.audio_int16_bytes)
            
            print(f"DEBUG: Synthesis finished. Sent {chunk_count} chunks total.")
        except Exception as e:
            print(f"ERROR: Piper synthesis failed: {e}")