"""TTS service wrapping VoxCPM core"""

import tempfile
import os
from typing import Optional

import numpy as np

import voxcpm
from .audio_utils import decode_audio_base64


class TTSService:
    """TTS service for VoxCPM model"""

    def __init__(self, model_id: str = "openbmb/VoxCPM2", device: str = "auto"):
        self.model: Optional[voxcpm.VoxCPM] = None
        self.model_id = model_id
        self.device = device
        self._loaded = False

    def load_model(self):
        """Load the VoxCPM model lazily"""
        if self._loaded:
            return

        device = None if self.device == "auto" else self.device
        self.model = voxcpm.VoxCPM.from_pretrained(
            self.model_id,
            optimize=True,
            device=device,
        )
        self._loaded = True

    def generate(
        self,
        text: str,
        mode: str,
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
        control_instruction: Optional[str] = None,
        cfg_value: float = 2.0,
        inference_timesteps: int = 10,
        normalize: bool = False,
        denoise: bool = False,
    ) -> tuple[np.ndarray, int]:
        """Generate audio from text.

        Args:
            text: Text to synthesize
            mode: Generation mode ("design", "clone", "continue", "combined")
            reference_audio: Base64 encoded reference audio
            reference_text: Text corresponding to reference audio
            control_instruction: Voice control instruction
            cfg_value: CFG guidance strength
            inference_timesteps: Number of inference steps
            normalize: Whether to normalize text
            denoise: Whether to denoise reference audio

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        self.load_model()

        ref_audio_path = None
        if reference_audio:
            audio_data, sr = decode_audio_base64(reference_audio)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                import soundfile as sf
                sf.write(f.name, audio_data, sr)
                ref_audio_path = f.name

        try:
            final_text = self._build_text(text, control_instruction, mode)

            generate_kwargs = dict(
                text=final_text,
                cfg_value=cfg_value,
                inference_timesteps=inference_timesteps,
                normalize=normalize,
                denoise=denoise,
            )

            if mode in ("clone", "combined") and ref_audio_path:
                generate_kwargs["reference_wav_path"] = ref_audio_path

            if mode == "continue" and ref_audio_path and reference_text:
                generate_kwargs["prompt_wav_path"] = ref_audio_path
                generate_kwargs["prompt_text"] = reference_text
                if mode == "combined":
                    generate_kwargs["reference_wav_path"] = ref_audio_path

            audio = self.model.generate(**generate_kwargs)
            return audio, self.model.tts_model.sample_rate
        finally:
            if ref_audio_path and os.path.exists(ref_audio_path):
                os.unlink(ref_audio_path)

    def _build_text(self, text: str, control: Optional[str], mode: str) -> str:
        """Build text with control instruction if needed"""
        if control and mode in ("design", "clone", "combined"):
            return f"({control}){text}"
        return text

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._loaded
