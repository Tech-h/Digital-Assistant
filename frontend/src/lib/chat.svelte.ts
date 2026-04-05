export type Message = { role: 'user' | 'assistant', text: string };

let socket: WebSocket | null = null;

// Svelte 5 reactive state
export const input = $state({
    messages: [] as Message[],
    inputText: '',
    loading: false
});

/**
 * Sends a text message to the backend via the saved WebSocket reference.
 */
export async function handleSend(text: string, isVoice: boolean = false) {
    if (!text.trim() || !socket) return;
    
    input.messages.push({ role: 'user', text });
    input.loading = true;
    
    // Send as a JSON object so the backend knows if it should speak
    socket.send(JSON.stringify({
        type: "text",
        content: text,
        is_voice: isVoice // Pass this along
    }));
}

/**
 * Called by the Central Hub (App.svelte) when a text response arrives.
 */
export function addAssistantResponse(text: string) {
    input.loading = false;
    input.messages.push({ role: 'assistant', text });
}

export function connect(ws: WebSocket) {
    socket = ws;
}

export function disconnect() {
    socket = null;
    input.loading = false;
}