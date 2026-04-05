
![alt text](/docs/image.png)
# Digital Assistant
Developing a voice activated AI assistant in Python using Ollama for LLM inference, featuring conversational memory, and an integrated speech recognition/text-to-speech pipeline. Implemented a custom event bus for decoupled, modular communication between components. Accessible via the Svelte web frontend interface hosted on personal Linux server, accessible across devices via private Tailscale network. 

## System Architecture
**Backend:** Built modularly in Python, easily change out the different parts to customize.
**Frontend** SvelteKit + Vite for a real-time reactive dashboard.
**Networking** Secure, zero-config access across devices via **Tailscale**.

## Tech Stack
* **Languages:** Python 3.13.11+, Typescript
* **Third-Party** 
    - Ollama (Local Hermes3:8b Model)
    - Faster-Whisper (STT: Audio transcription model)
    - Piper-TTS (Text-To-Speech Model)
    - FastAPI (Allows for the Frontend/Backend inter-communication)
    - SvelteKit (Svelte 5)

## Getting Started
```bash
git clone [https://github.com/Tech-h/Digital-Assistant.git]
cd [Digital_Assistant]
```

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
python digital_assistant.py
```

### Voce Synthesis (Piper-TTS)
This project uses **Piper** for fast, local, and private text-to-speech synthesis. It was chose for being lightweight as a precaution during development, but will be replaced with a more naturally sounding TTS in a future update. 

Its recommended to obtain the voices from **Hugging Face*** and to place them into the /data/source_models folder

```bash
https://huggingface.co/rhasspy/piper-voices/tree/main
```

## License
'Digital Assistant' is MIT licensed.