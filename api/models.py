"""Pydantic models for API requests and responses"""

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    """Error detail model"""

    code: str
    message: str


class TTSRequest(BaseModel):
    """TTS synthesis request model"""

    text: str = Field(..., min_length=1, max_length=1000, description="Text to synthesize")
    control_instruction: str | None = Field(
        default=None, max_length=200, description="Voice control instruction"
    )
    reference_audio: str | None = Field(
        default=None, description="Base64 encoded WAV audio for reference"
    )
    reference_text: str | None = Field(
        default=None, max_length=500, description="Text corresponding to reference audio"
    )
    cfg_value: float = Field(default=2.0, ge=1.0, le=3.0, description="CFG guidance strength")
    inference_timesteps: int = Field(
        default=10, ge=1, le=50, description="Number of inference steps"
    )
    normalize: bool = Field(default=False, description="Whether to normalize text")
    denoise: bool = Field(default=False, description="Whether to denoise reference audio")
    output_format: str | None = Field(
        default=None, pattern="^(base64|file)$", description="Output format: base64 or file"
    )


class TTSResponse(BaseModel):
    """TTS synthesis response model"""

    model_config = ConfigDict(protected_namespaces=())

    success: bool
    audio: str | None = None
    sample_rate: int | None = None
    duration_seconds: float | None = None
    mode: str | None = None
    model_id: str | None = None
    error: ErrorDetail | None = None
    content_type: str | None = None


class HealthResponse(BaseModel):
    """Health check response model"""

    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    model_id: str | None = None
