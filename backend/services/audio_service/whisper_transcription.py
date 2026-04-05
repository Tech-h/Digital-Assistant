# === Standard Library ===
import threading

# === Third-Party ===
import numpy as np
from faster_whisper import WhisperModel

# === Project ===
from backend.event_bus import Events


class WhisperTranscription:
    def __init__(self):
        self.model = WhisperModel(
            model_size_or_path='base',
            device='cpu', # Options: cpu cuda
            compute_type='int8', # Options: int8 float16
            local_files_only=False
        )
        
        self._lock = threading.Lock()
        
        Events.complete_utterance.connect(self.handle_new_utterance)


    def handle_new_utterance(self, audio: np.ndarray) -> None:
        # beam_size=1 is essential for real-time. It uses 'Greedy' 
        # decoding, which is significantly faster than searching for 
        # multiple word possibilities.
        segments, _ = self.model.transcribe(
            audio, 
            beam_size=1,
            # Secondary filter to ensure Whisper doesn't 
            # hallucinate on noise
            vad_filter=True 
        )
        
        # Collapses the generator into a single string.
        text: str = "".join(s.text for s in segments).strip()
        
        Events.send_transcription.emit(text)

    def stop(self) -> None:
        with self._lock:
            if hasattr(self, 'model'):
                del self.model