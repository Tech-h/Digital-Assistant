# === Standard Library ===
import threading, queue, logging
from typing import Optional

# === 3rd Party === 
from piper import PiperVoice, SynthesisConfig

# === Project ===
from backend.services.voice_service.tts_engine import TTSEngine
from backend.services.voice_service.process_text import ProcessText
import backend.services.voice_service.voice_config as vc
from backend.services.voice_service.configure_system import ConfigureSystem
from backend.event_bus import Events

class VoiceController:
    """
    Manages the voice synthesis pipeline.
    Routes LLM chunks into sentences, then into the TTS Engine for web streaming.
    """
    def __init__(self) -> None:
        print("DEBUG: VoiceController Init - Loading Piper Model...")
        model_path = str(vc.PIPER_MODEL) 
        self.voice = PiperVoice.load(model_path)
        
        # Helper Sub-modules
        self.configure_system = ConfigureSystem()
        self.process_text = ProcessText()
        self.tts_engine: Optional[TTSEngine] = None
        
        # Threading Control
        self.running: bool = False
        self._playback_thread: Optional[threading.Thread] = None
        
        # Event Bus Connections
        Events.llm_chunk.connect(self.receive_chunk)
        Events.llm_response_finished.connect(self.finalize_speech)
        print("DEBUG: VoiceController Init - Complete.")
        
    def start(self) -> None:
        if self.running: return
        print("DEBUG: VoiceController start() called.")

        try:
            self.running = True
            synthesis_config: SynthesisConfig = self.configure_system.get_synthesis_config()
            
            # Initialize the TTS worker
            self.tts_engine = TTSEngine(
                voice=self.voice, 
                synthesis_config=synthesis_config
            )
            print("DEBUG: VoiceController - TTSEngine successfully initialized.")
            
            # Start the background thread that watches the speech_queue
            self._playback_thread = threading.Thread(target=self._speech_loop, daemon=True)
            self._playback_thread.start()
        except Exception as e:
            print(f"ERROR: VoiceController start() failed: {e}")

    def stop(self) -> None:
        self.running = False
        if self._playback_thread:
            self._playback_thread.join(timeout=1.0)

    def receive_chunk(self, chunk: str) -> None:
        # print(f"DEBUG: VoiceController got chunk: {repr(chunk)}") # Uncomment if you want to see every syllable
        self.process_text.process_chunk(chunk)
    
    def finalize_speech(self, text: str) -> None:
        print(f"DEBUG: LLM finished response. Finalizing TTS buffer...")
        self.process_text.finalize()

    def _speech_loop(self) -> None:
        """
        Continuously pulls complete sentences from the queue and 
        passes them to the engine for synthesis.
        """
        print("DEBUG: VoiceController _speech_loop thread is ALIVE and waiting for sentences.")
        while self.running:
            try:
                # 0.5s timeout allows the thread to check self.running periodically
                sentence = self.process_text.speech_queue.get(timeout=0.5)
                print(f"DEBUG: _speech_loop pulled sentence from queue: {repr(sentence)}")
                
                if self.tts_engine and sentence:
                    self.tts_engine.speak(sentence)
                elif not self.tts_engine:
                    print("ERROR: tts_engine is None inside _speech_loop!")
                
                self.process_text.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"ERROR: VoiceController Error in playback loop: {e}")
        
        print("DEBUG: VoiceController _speech_loop thread is CLOSING.")

    def clear_queue(self) -> None:
        with self.process_text.speech_queue.mutex:
            self.process_text.speech_queue.queue.clear()