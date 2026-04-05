# === Standard Library ===
from pathlib import Path
from typing import Iterator

# === Project ===
from backend.event_bus import Events
from backend.services.llm_service.response_generation import ResponseGenerator
from backend.services.llm_service.conversational_memory import ConversationalMemory

OLLAMA_HOST = "http://localhost:11434"
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
CONVO_HISTORY_FILE = DATA_DIR / "conversation_history.txt"

class LLMController:
    def __init__(self) -> None:
        self.response_generator = ResponseGenerator(
            model="hermes3:8b",
            host=OLLAMA_HOST,
            system_prompt="You are Cortana, a highly intelligent and helpful digital assistant.",
            temp=0.8, 
            num_ctx=4096
        )

        if CONVO_HISTORY_FILE:
            self.convo_memory = ConversationalMemory(CONVO_HISTORY_FILE)
        else: 
            print("Missing Memory File!")
        
        Events.send_transcription.connect(self._prompt_llm)
    
    def start(self) -> None:
        self.convo_memory.start()
    
    def stop(self) -> None:
        self.convo_memory.stop()

    def _prompt_llm(self, prompt: str) -> None:
        self.convo_memory.add_user_prompt(prompt)
        
        response_iterator: Iterator[str] = self.response_generator.generate_response(
            self.convo_memory.get_history()
        )
        
        chunks = []
        for chunk in response_iterator:
            chunks.append(chunk)
            Events.llm_chunk.emit(chunk)
        
        full_response_text = "".join(chunks)
        
        Events.llm_response_finished.emit(full_response_text)
        self.convo_memory.add_llm_response(full_response_text)