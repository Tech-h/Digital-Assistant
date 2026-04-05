from pathlib import Path

# ==============================================================================
# GLOBAL PATHS
# ==============================================================================
# Resolves to: root/app/components/llm_service -> root/
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
PIPER_MODEL = ROOT_DIR / "data" / "source_models" / "en_US-lessac-medium.onnx"

PIPER_MODEL_NAME = "en_US-lessac-medium.onnx"
PIPER_VOLUME = 0.5
PIPER_LENGTH_SCALE = 1.0   # Speed: >1.0 slower, <1.0 faster
PIPER_NOISE_SCALE = 0.667  # Phoneme variability (Default is usually 0.667)
PIPER_NOISE_W_SCALE = 0.8  # Intonation variability (Default is usually 0.8)
PIPER_NORMALIZE = False