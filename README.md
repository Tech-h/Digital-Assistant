
![alt text](/docs/image2.png)
# Digital Assistant
Developing a voice activated AI assistant in Python using Ollama for LLM inference, featuring conversational memory, and an integrated speech recognition/text-to-speech pipeline. Implemented a custom event bus for decoupled, modular communication between components. Accessible via the Svelte web frontend interface hosted on personal Linux server, accessible across devices via private Tailscale network. 

## System Architecture
* **Backend:** 
    Built modularly in Python, easily change out the different parts to customize.
* **Frontend:** 
    SvelteKit + Vite for a real-time reactive dashboard.
* **Networking:** 
    Secure, zero-config access across devices via **Tailscale**.

## Tech Stack
* **Languages:** Python 3.13.11+, Typescript
* **Third-Party** 
    - Ollama (Local Hermes3:8b Model)
    - Faster-Whisper (STT: Audio transcription model)
    - Piper-TTS (Text-To-Speech Model)
    - FastAPI (Allows for the Frontend/Backend inter-communication)
    - SvelteKit (Svelte 5 for the website interface)
    - Node.js

## Getting Started

### Download and Setup Instructions
```bash
git clone https://github.com/Tech-h/Digital-Assistant.git
cd Digital_Assistant
```

```bash
python -m venv .venv

.venv\Scripts\activate # On Windows
source .venv/bin/activate  # On Linux/Mac

pip install -r requirements.txt

cd frontend
npm install # Generates node_modules folder for dependencies
npm install @ricky0123/vad-web

# If you want to start the front-end from scratch:
cd frontend
npm create vite@latest . -- --template svelte-ts
```

### Running the Assistant
Running the assistant first requires downloading and **opening** the ollama app (and nothing else as we just need access to the ollama port). 

Then run these commands:
```bash
# In one terminal:
python Digital_Assistant.py

# In a second terminal:
cd frontend
npm run dev
```


## Voice Synthesis (Piper-TTS)
This project uses **Piper** for fast, local, and private text-to-speech synthesis. It was chosen for being lightweight as a precaution during development, but will be replaced with a more natural-sounding TTS in a future update. 

It's recommended to obtain the voices from **Hugging Face** and to place them into the /data/source_models folder

```bash
https://huggingface.co/rhasspy/piper-voices/tree/main
```

## RoadMap
This assistant is being built as an answer to my childhood dream of having a digital companion, one that helps with day-to-day tasks while also serving as a creative and invention-focused tool. The following roadmap outlines the features I want to implement in order to produce an AI assistant that feels like it exists persistently, unlike traditional LLM interface solutions. Made in the vision of Jarvis (Iron-man) and Cortana (Halo).

As these updates are completed, they will be removed from the Roadmap, and the rest of the README adjusted to reflect the new features. With new updates being added as I continue to develop this assistant. 

### Large Updates
* Implement speaker diarization and speaker detection, with the aim to allow for the assistant to recognize people it 'meets', with being able to 
remember them for the next interaction at any other time. 
* Implement a new and robust memory system that makes use of vectorized memory and associative metadata attached to each vector of memory. This will allow for the assistant to pull in a wider variety and scope of memories from its database, with the aim to reduce tunnel vision from the assistant. The metadata will use a system of tags in order to link towards multiple geographies of vectors.
* An assistant is useless if it can't actually do anything, but hand implementing every single feature, especially if the request is novel, would eat up a large amount of time and resources. Which is why the ability for the assistant to procedually program its own new abilities (within reason) is a core feature that I want to implement.

### Minor Updates
* Adjust audio output of the TTS to only generate if the mic has been toggled.
* There should be two audio level bars, one for the user, and one for the assistant (though implemented in a more visually expressive way).
* Thread assignment by group for Signal Objects at initialization for a smoother delegation of tasks and to lower the possibility of race conditions.
* Implement a performance profiling system in order to detect memory leaks and allow for performance optimization. 
* Allow for the assistant to be interrupted mid-sentence by the user. 
* Show the users spoken sentences as a text-prompt within the history as well, rather than just the LLMs outputs and written user inputs.
* Test out different llms and test which one responds the best to a series of tests for my specific project requirements.

### Possible Updates
* * Implement social-emotional intelligence. Meaning the assistant can now know how the user is feeling or how they spoke to the assistant or anyone else.
The goal is for the assistant to be able to use these data points to process the conversation on a higher level, creating a faux understanding similar to
a humans.
    * Detects emotions with a small modal. 
    * Detects volume. 
    * Detects speech length.
    * Hesitency / uncertaincy (uh, umm, maybe... like)
*Implement an audio classification model to detect non voiced sounds, which should help build context awareness around what the user is currently doing. As well as a visual model to process camera data, where the linkage of on video data and audio data should help the assistant build a conceptual understanding of what it views in terms of generating a timeline of events. 
* For the metadata in the vector-memory database, the contents of which will include salience (how much a memory stands out) scores and emotional data for creating a hierarchical memory organization process to mimic how human's draw upon thier own memories.

## License
MIT license