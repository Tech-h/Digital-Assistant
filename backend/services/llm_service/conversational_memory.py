# === Standard Library === 
import time, threading
from pathlib import Path
from typing import Optional


class ConversationalMemory:
    def __init__(self, convo_memory_file: Path) -> None:
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._num_writes: int = 0
        self._entry_threshold: int = 20 
        self._convo_memory_file: Path = convo_memory_file 
        self._convo_history: str = ""
    
    def start(self) -> None:
        self._running = True
        self._fill_convo_history()
        self._thread = threading.Thread(target=self._mem_process_loop, daemon=False)
        self._thread.start()
    
    def stop(self) -> None:
        self._running = False
        self._save_to_disk()
    
    def _save_to_disk(self) -> None:
        """Standard method to persist current state to the file."""
        with self._lock:
            self._convo_memory_file.write_text(self._convo_history)
            
    def add_user_prompt(self, prompt: str) -> None:
        with self._lock:
            self._num_writes += 1
            self._convo_history += f"<|im_start|>user\n{prompt}<|im_end|>\n"
    
    def add_llm_response(self, response: str) -> None:
        with self._lock:
            self._num_writes += 1
            self._convo_history += f"<|im_start|>assistant\n{response}<|im_end|>\n"
    
    def get_history(self) -> str:
        with self._lock: 
            return self._convo_history
        
    def _mem_process_loop(self) -> None:
        while self._running:
            needs_save = False
            with self._lock:
                # Check if new data to save
                needs_save = self._num_writes > 0
                
            if needs_save:
                self._shift_window() 
                with self._lock:
                    self._num_writes = 0
            
            time.sleep(5) 

    def _fill_convo_history(self) -> None:
        if self._convo_memory_file.exists():
            self._convo_history = self._convo_memory_file.read_text()
        else:
            self._convo_history = ""
            self._convo_memory_file.parent.mkdir(parents=True, exist_ok=True)
            self._convo_memory_file.write_text("")

    def _shift_window(self) -> None:
        with self._lock:
            parts = self._convo_history.split("<|im_start|>")
            messages = ["<|im_start|>" + p for p in parts if p.strip()]
            
            if len(messages) > self._entry_threshold:
                retained_messages = messages[-self._entry_threshold:] 
                self._convo_history = "".join(retained_messages)
                
        self._save_to_disk()