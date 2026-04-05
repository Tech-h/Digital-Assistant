import re
import queue
import threading

class ProcessText:
    def __init__(self) -> None:
        self.text_buffer = ""
        self.speech_queue = queue.Queue()
        
        self.split_pattern = re.compile(r'([.!?:\n]+)')
        
        # ADDED: A lock to prevent fast-arriving LLM chunks from 
        # tripping over each other in the ThreadPool
        self._lock = threading.Lock()
    
    def process_chunk(self, chunk: str) -> None:
        """Appends new text and pushes completed sentences to the speech queue."""
        if not chunk:
            return
            
        # The lock ensures only one thread can modify the buffer at a time
        with self._lock:
            self.text_buffer += chunk

            if self.split_pattern.search(self.text_buffer):
                parts = self.split_pattern.split(self.text_buffer)
                
                # We need at least 3 parts to have a complete 
                # Sentence + Punctuation + Remaining
                while len(parts) > 2:
                    sentence_text = parts.pop(0)
                    punctuation = parts.pop(0)
                    
                    full_sentence = (sentence_text + punctuation).strip()
                    if full_sentence:
                        print(f"DEBUG: ProcessText built a full sentence: {repr(full_sentence)}")
                        self.speech_queue.put(full_sentence)
                
                # Put the remaining incomplete tail back into the buffer
                self.text_buffer = "".join(parts)
    
    def finalize(self) -> None:
        with self._lock:
            remaining = self.text_buffer.strip()
            if remaining:
                print(f"DEBUG: ProcessText finalizing leftover buffer: {repr(remaining)}")
                self.speech_queue.put(remaining)
            self.text_buffer = ""