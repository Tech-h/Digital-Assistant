# === Standard Library ===
import threading, logging
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor

# === Third-Party ===
import numpy as np

# === Global Worker Pool ===
_dispatch_pool = ThreadPoolExecutor(
    max_workers=4, thread_name_prefix="SignalWorker"
    )


class Signal:
    def __init__(self, name: str, **schema: type[Any]) -> None:
        self.name: str = name
        self.schema: dict[str, type[Any]] = schema
        self._listeners: list[Callable[..., Any]] = []
        self._lock = threading.Lock()

    def connect(self, callback: Callable[..., Any]) -> None:
        with self._lock:
            self._listeners.append(callback)
    
    def disconnect(self, callback: Callable[..., Any]) -> None:
        with self._lock:
            if callback in self._listeners:
                self._listeners.remove(callback)
                
    def emit(self, *args: Any) -> None:
        self._validate_schema(*args)
        
        with self._lock:
            listeners_snapshot = self._listeners[:]
            
        for callback in listeners_snapshot:
            _dispatch_pool.submit(self._run_safe, callback, *args)
                

    def _run_safe(self, callback: Callable, *args: Any) -> None:
        try:
            callback(*args)
        except Exception as e:
            logging.error(
                f"Error in signal handler for {self.name}\n" 
                f"    Handler: {callback.__name__}\n"
                f"    Error: {e}",
                exc_info=True
            )

    def _validate_schema(self, *args: Any) -> None:
        if len(args) != len(self.schema):
            logging.error(
                f"[{self.name}] Argument count mismatch! "
                f"Expected {len(self.schema)} ({list(self.schema.keys())}), got {len(args)}"
            )
            return
            
        for val, (arg_name, expected_type) in zip(args, self.schema.items()):
            if not isinstance(val, expected_type):
                type_name: str = getattr(expected_type, '__name__', str(expected_type))
                got_name: str = type(val).__name__
                logging.error(
                    f"[{self.name}] Type mismatch for '{arg_name}'! "
                    f"Expected {type_name}, got {got_name}"
                )


class _EventBus:
    complete_utterance = Signal("complete_utterance", text=np.ndarray)
    send_transcription = Signal("send_transcription", text=str)
    
    llm_chunk = Signal("llm_chunk", chunk=str)
    llm_response_finished = Signal("llm_response_finished", text=str)
    
    speech_finalized = Signal("speech_finalized", status=bool)
    
    memory_updated = Signal("memory_updated")
    audio_out = Signal("audio_out", audio=bytes)

Events = _EventBus()