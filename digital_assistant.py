# === Standard Library ===
import time, threading, uvicorn

# === Project ===
from backend.web_interface import WebInterface
from backend.services.llm_service.llm_controller import LLMController
from backend.services.voice_service.voice_controller import VoiceController
from backend.services.audio_service.audio_controller import AudioController


class DigitalAssistant:
    def __init__(self) -> None:
        self._running = True
        
        self.web_interface = WebInterface()
        
        self.audio_controller = AudioController()
        self.llm_controller = LLMController()
        self.voice_controller = VoiceController()
        
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._running = False
  
        self.llm_controller.stop()
        self.voice_controller.stop()
        self.audio_controller.stop()
  
  
    def start_processing(self) -> None:
        web_thread = threading.Thread(target=self._run_web_server, daemon=True)
        web_thread.start()

        self.audio_controller.start()
        self.llm_controller.start()
        self.voice_controller.start()
        
        try:
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self._running = False
    
    def _run_web_server(self):
        uvicorn.run(self.web_interface.interface, host="0.0.0.0", port=8000, log_level="info")
        


if __name__ == "__main__":
    with DigitalAssistant() as assistant:
        assistant.start_processing()