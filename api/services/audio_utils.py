"""Audio utilities for base64 encoding/decoding"""

import base64
import io
from typing import Tuple

import numpy as np
import soundfile as sf


def decode_audio_base64(encoded: str) -> Tuple[np.ndarray, int]:
    """Decode base64 encoded audio to numpy array.

    Args:
        encoded: Base64 encoded WAV audio string

    Returns:
        Tuple of (audio_data, sample_rate)
    """
    wav_bytes = base64.b64decode(encoded)
    audio_io = io.BytesIO(wav_bytes)
    audio, sr = sf.read(audio_io, dtype="float32")
    return audio, sr


def encode_audio_base64(audio: np.ndarray, sample_rate: int) -> str:
    """Encode numpy audio array to base64 WAV string.

    Args:
        audio: Audio data as numpy array
        sample_rate: Sample rate of the audio

    Returns:
        Base64 encoded WAV string
    """
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format="WAV", subtype="PCM_16")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
