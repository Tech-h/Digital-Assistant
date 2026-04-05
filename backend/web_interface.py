# === Standard Library ===
import asyncio, json

# === Third-Party ===
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# === Project === 
from backend.event_bus import Events


class WebInterface():
    def __init__(self) -> None:
        self.interface = FastAPI()
        self.interface.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_methods=["*"], 
            allow_headers=["*"]
        )
        self.interface.add_api_websocket_route("/chat", self.chat)
        
        self._websocket: WebSocket | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

        Events.llm_response_finished.connect(self.respond_text)
        Events.audio_out.connect(self.respond_audio)


    async def chat(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._websocket = websocket
        self._loop = asyncio.get_running_loop() 
        
        try:
            while True:
                message = await websocket.receive()

                if message.get("type") == "websocket.disconnect": break

                text_data = message.get("text")
                bytes_data = message.get("bytes")

                if text_data:
                    data = json.loads(text_data)
                    Events.send_transcription.emit(data["content"])
                
                elif bytes_data:
                    audio_array = np.frombuffer(bytes_data, dtype=np.float32)
                    if len(audio_array) > 1600:
                        Events.complete_utterance.emit(audio_array)

        except (WebSocketDisconnect, RuntimeError) as e:
            print(f"DEBUG: WebSocket ended: {e}")
        except Exception as e:
            print(f"ERROR: WebSocket loop crashed: {e}")
        finally:
            self._websocket = None
            print("DEBUG: WebSocket Cleanup Complete.")

    def respond_text(self, text: str) -> None:
        if self._websocket and self._loop:
            asyncio.run_coroutine_threadsafe(
                self._websocket.send_text(text), 
                self._loop
            )

    def respond_audio(self, audio: bytes) -> None:
        if self._websocket and self._loop:
            asyncio.run_coroutine_threadsafe(
                self._websocket.send_bytes(audio), 
                self._loop
            )
        else:
            print("DEBUG: !!! Cannot send audio. WebSocket is not connected.")