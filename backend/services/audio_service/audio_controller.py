# === Project ===
from .whisper_transcription import WhisperTranscription


class AudioController:
    def __init__(self) -> None:
        self.whisper = WhisperTranscription()
        
        
    def start(self) -> None:
        pass
     
    def stop(self) -> None:
        self.whisper.stop()
    