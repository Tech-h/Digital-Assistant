import backend.services.voice_service.voice_config as vc

from piper import SynthesisConfig

class ConfigureSystem():
    def get_synthesis_config(self) -> SynthesisConfig:
        return SynthesisConfig(
            volume=vc.PIPER_VOLUME, 
            length_scale=vc.PIPER_LENGTH_SCALE,
            noise_scale=vc.PIPER_NOISE_SCALE, 
            noise_w_scale=vc.PIPER_NOISE_W_SCALE,  
        )