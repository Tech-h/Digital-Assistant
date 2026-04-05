<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import * as chat from './lib/chat.svelte';
    import * as audio from './lib/audio.svelte';

    let ws: WebSocket | null = null;

    onMount(() => {
        // 1. Establish Connection
        ws = new WebSocket('ws://localhost:8000/chat');

        ws.onopen = () => {
            console.log("WebSocket Hub: Connected");
            chat.connect(ws!);
            audio.connect(ws!);
        };

        // 2. CENTRAL ROUTING LOGIC
        // This ensures chat and audio don't overwrite each other's listeners
        ws.onmessage = async (event) => {
            if (typeof event.data === 'string') {
                // Incoming LLM Text
                chat.addAssistantResponse(event.data);
            } else {
                // Incoming Piper Audio (Binary)
                const buffer = await event.data.arrayBuffer();
                audio.playRawAudioChunk(buffer);
            }
        };

        ws.onerror = (err) => {
            console.error("WebSocket Hub: Error", err);
            chat.addAssistantResponse("Connection Error. Ensure the backend server is running.");
        };

        ws.onclose = () => {
            console.warn("WebSocket Hub: Closed");
        };
    });

    onDestroy(() => {
        chat.disconnect();
        audio.disconnect();
        audio.stopMicrophone();
        if (ws) ws.close();
    });

    async function handleKeyDown(e: KeyboardEvent) {
        // Prevent sending if Enter+Shift (new line) or if Mic is active
        if (e.key === 'Enter' && !e.shiftKey && !audio.audioStatus.isActive) {
            e.preventDefault();
            const text = chat.input.inputText.trim();
            if (!text) return;

            chat.input.inputText = ''; 
            await chat.handleSend(text);
        }
    }
</script>

<main>
    <div class="vbox">
        <header><h1>Digital Assistant</h1></header>

        <div class="conversation_history">
            {#each chat.input.messages as message}
                <div class="message {message.role}">
                    {message.text}
                </div>
            {/each}
            
            {#if chat.input.loading}
                <div class="message assistant typing">...</div>
            {/if}
        </div>

        <div class="input_box">
            {#if audio.audioStatus.isActive}
                <div class="visualizer">
                    {#each audio.audioStatus.cellColors as color}
                        <div class="cell {color}"></div>
                    {/each}
                </div>
            {/if}

            <div class="input_wrapper">
                <div
                    class="input_area"
                    contenteditable="true"
                    role="textbox"
                    tabindex="0"
                    bind:textContent={chat.input.inputText}
                    onkeydown={handleKeyDown}
                ></div>
                
                <div class="input_controls">
                    {#if audio.audioStatus.isSpeaking}
                        <span class="listening_indicator">
                            ● Detecting Speech...
                        </span>
                    {/if}

                    <button 
                        class="mic_button" 
                        class:active={audio.audioStatus.isActive} 
                        onclick={() => audio.toggleMicrophone()}
                    >
                        🎤 {audio.audioStatus.isActive ? 'Stop Mic' : 'Mic'}
                    </button>
                </div>
            </div>
        </div>
    </div>
</main>

<style>
    main {
        height: 100vh;
        display: flex;
        background-color: #0f172a;
        color: #f8fafc;
        font-family: system-ui, -apple-system, sans-serif;
    }
    .vbox {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        width: 100%;
        height: 100%;
    }
    .conversation_history {
        flex: 1;
        overflow-y: auto;
        width: 75%;
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 20px 0;
    }
    .message {
        padding: 10px 14px;
        border-radius: 12px;
        max-width: 80%;
        line-height: 1.5;
        word-wrap: break-word;
    }
    .message.user {
        align-self: flex-end;
        background: #3b82f6;
    }
    .message.assistant {
        align-self: flex-start;
        background: #1e293b;
    }
    .message.typing {
        color: #64748b;
        font-style: italic;
    }
    .input_box {
        display: flex;
        flex-direction: column;
        width: 75%;
        margin-bottom: 24px;
        gap: 8px;
    }
    .visualizer {
        display: flex;
        gap: 4px;
        height: 14px;
        padding: 0 12px;
    }
    .cell {
        flex: 1;
        border-radius: 2px;
        transition: background-color 0.1s ease;
    }
    .cell.inactive { background: #1e293b; }
    .cell.green { background: #22c55e; }
    .cell.yellow { background: #eab308; }
    .cell.red { background: #ef4444; }

    .input_wrapper {
        display: flex;
        flex-direction: column;
        border: 1px solid #334155;
        background: #1e293b;
        border-radius: 12px;
        padding: 12px;
    }
    .input_area {
        flex: 1;
        outline: none;
        min-height: 44px;
        max-height: 200px;
        overflow-y: auto;
    }
    .input_controls {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding-top: 8px;
        border-top: 1px solid #334155;
        margin-top: 8px;
    }
    .listening_indicator {
        color: #22c55e;
        font-size: 0.9rem;
        font-weight: 600;
        margin-right: auto;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
    .mic_button {
        padding: 6px 16px;
        border-radius: 8px;
        border: 1px solid #475569;
        background: transparent;
        cursor: pointer;
        color: inherit;
        font-weight: 500;
        transition: all 0.2s;
    }
    .mic_button:hover { background: #334155; }
    .mic_button.active {
        background: #ef4444;
        border-color: #ef4444;
    }
</style>