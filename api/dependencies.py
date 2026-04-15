"""FastAPI dependencies"""

from functools import lru_cache

from .config import APISettings
from .services.tts_service import TTSService


@lru_cache
def get_settings() -> APISettings:
    """Get cached API settings"""
    return APISettings()


@lru_cache
def get_tts_service() -> TTSService:
    """Get cached TTS service instance"""
    settings = get_settings()
    return TTSService(model_id=settings.model_id, device=settings.device)
