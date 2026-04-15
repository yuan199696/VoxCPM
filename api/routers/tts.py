"""TTS router"""

import io
from typing import Union

from fastapi import APIRouter, Response

from ..models import TTSRequest, TTSResponse, ErrorDetail
from ..services.tts_service import TTSService
from ..services.audio_utils import encode_audio_base64
from ..dependencies import get_tts_service, get_settings
import soundfile as sf


router = APIRouter()


def detect_mode(request: TTSRequest) -> str:
    """Detect generation mode based on request parameters"""
    has_ref = request.reference_audio is not None
    has_ref_text = request.reference_text is not None
    has_control = request.control_instruction is not None

    if has_ref and has_ref_text:
        return "continue"
    elif has_ref:
        return "clone"
    elif has_control:
        return "combined"
    else:
        return "design"


@router.post("/tts", response_model=None)
async def text_to_speech(request: TTSRequest) -> Union[TTSResponse, Response]:
    """Text-to-Speech synthesis endpoint.

    Automatically detects the generation mode based on provided parameters:
    - Voice Design: text + control_instruction only
    - Voice Cloning: text + reference_audio (no reference_text)
    - Voice Continuation: text + reference_audio + reference_text

    When output_format is "file", returns the audio as a WAV file directly.
    When output_format is "base64", returns the audio as a base64 encoded string in JSON.
    """
    try:
        mode = detect_mode(request)

        tts_service = get_tts_service()
        settings = get_settings()

        audio, sample_rate = tts_service.generate(
            text=request.text,
            mode=mode,
            reference_audio=request.reference_audio,
            reference_text=request.reference_text,
            control_instruction=request.control_instruction,
            cfg_value=request.cfg_value,
            inference_timesteps=request.inference_timesteps,
            normalize=request.normalize,
            denoise=request.denoise,
        )

        output_format = request.output_format or settings.default_output_format

        if output_format == "file":
            buffer = io.BytesIO()
            sf.write(buffer, audio, sample_rate, format="WAV", subtype="PCM_16")
            buffer.seek(0)

            return Response(
                content=buffer.getvalue(),
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=synthesized.wav",
                    "X-Sample-Rate": str(sample_rate),
                    "X-Duration": str(len(audio) / sample_rate),
                    "X-Mode": mode,
                },
            )
        else:
            audio_output = encode_audio_base64(audio, sample_rate)
            return TTSResponse(
                success=True,
                audio=audio_output,
                sample_rate=sample_rate,
                duration_seconds=len(audio) / sample_rate,
                mode=mode,
                model_id=tts_service.model_id,
                content_type="audio/wav",
            )

    except Exception as e:
        return TTSResponse(
            success=False,
            error=ErrorDetail(code="GENERATION_ERROR", message=str(e)),
        )
