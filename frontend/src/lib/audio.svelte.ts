import { MicVAD } from '@ricky0123/vad-web';

interface AudioState {
    audioContext: AudioContext;
    analyser: AnalyserNode;
    stream: MediaStream;
    source: MediaStreamAudioSourceNode;
}

// ============================================================================
// REACTIVE STATE
// ============================================================================
export const audioStatus = $state({
    isActive: false,
    isSpeaking: false,
    cellColors: Array(32).fill('inactive')
});

let activeAudioState: AudioState | null = null;
let animationFrameId: number | null = null;
let vad: any = null;
let socket: WebSocket | null = null;

// Playback state for Assistant's Voice (Piper)
let playbackCtx: AudioContext | null = null;
let nextStartTime: number = 0;

const PIPER_SAMPLE_RATE = 22050; 
const NUM_CELLS = 32;

// ============================================================================
// WEBSOCKET & PLAYBACK LOGIC
// ============================================================================
export function connect(ws: WebSocket) {
    socket = ws;
}

export function disconnect() {
    socket = null;
    if (playbackCtx) {
        playbackCtx.close();
        playbackCtx = null;
    }
}

/**
 * Converts Int16 PCM (from Python) to Float32 and schedules gapless playback.
 */
export async function playRawAudioChunk(arrayBuffer: ArrayBuffer) {
    if (!playbackCtx) {
        playbackCtx = new AudioContext({ sampleRate: PIPER_SAMPLE_RATE });
        nextStartTime = playbackCtx.currentTime;
    }

    if (playbackCtx.state === 'suspended') await playbackCtx.resume();

    const int16Data = new Int16Array(arrayBuffer);
    const float32Data = new Float32Array(int16Data.length);
    
    for (let i = 0; i < int16Data.length; i++) {
        float32Data[i] = int16Data[i] / 32768.0;
    }

    const buffer = playbackCtx.createBuffer(1, float32Data.length, PIPER_SAMPLE_RATE);
    buffer.getChannelData(0).set(float32Data);

    const source = playbackCtx.createBufferSource();
    source.buffer = buffer;
    source.connect(playbackCtx.destination);

    const startTime = Math.max(nextStartTime, playbackCtx.currentTime);
    source.start(startTime);
    nextStartTime = startTime + buffer.duration;
}

// ============================================================================
// MICROPHONE CONTROL
// ============================================================================
export async function toggleMicrophone(): Promise<void> {
    audioStatus.isActive ? stopMicrophone() : await startMicrophone();
}

export async function startMicrophone(): Promise<void> {
    try {
        activeAudioState = await setupAudioSystem();
        audioStatus.isActive = true;

        const dataArray = new Uint8Array(activeAudioState.analyser.frequencyBinCount);
        animate(activeAudioState.analyser, dataArray);

        vad = await MicVAD.new({
            getStream: async () => activeAudioState!.stream,
            baseAssetPath: "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.29/dist/",
            onnxWASMBasePath: "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.22.0/dist/",
            onSpeechStart: () => { audioStatus.isSpeaking = true; },
            onSpeechEnd: (audio: Float32Array) => { 
                audioStatus.isSpeaking = false;
                if (socket?.readyState === WebSocket.OPEN) {
                    socket.send(audio.buffer as any);
                }
            },
            onVADMisfire: () => { audioStatus.isSpeaking = false; }
        });

        vad.start();
    } catch (err) {
        console.error("Failed to start microphone:", err);
        stopMicrophone();
    }
}

export function stopMicrophone(): void {
    audioStatus.isActive = false;
    audioStatus.isSpeaking = false;
    if (animationFrameId) cancelAnimationFrame(animationFrameId);
    if (vad) { vad.pause(); vad.destroy(); vad = null; }
    if (activeAudioState) {
        activeAudioState.stream.getTracks().forEach(t => t.stop());
        activeAudioState.audioContext.close();
        activeAudioState = null;
    }
    audioStatus.cellColors = Array(NUM_CELLS).fill('inactive');
}

async function setupAudioSystem(): Promise<AudioState> {
    const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { noiseSuppression: true, echoCancellation: true, autoGainControl: true } 
    });
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    return { audioContext, analyser, stream, source };
}

function animate(analyser: AnalyserNode, dataArray: Uint8Array): void {
    if (!audioStatus.isActive) return;
    analyser.getByteFrequencyData(dataArray as any);
    const rms = Math.sqrt(dataArray.reduce((acc, val) => acc + val * val, 0) / dataArray.length);
    const level = Math.min(Math.pow(rms / 255, 0.4) * 1.2, 1);
    
    audioStatus.cellColors = Array.from({ length: NUM_CELLS }).map((_, i) => {
        const cellLevel = (i / NUM_CELLS) * 0.8;
        if (level >= cellLevel) {
            if (cellLevel > 0.75) return 'red';
            if (cellLevel > 0.5) return 'yellow';
            return 'green';
        }
        return 'inactive';
    });
    animationFrameId = requestAnimationFrame(() => animate(analyser, dataArray));
}