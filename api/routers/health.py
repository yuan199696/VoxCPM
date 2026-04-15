"""Health check router"""

from fastapi import APIRouter

from ..models import HealthResponse
from ..dependencies import get_tts_service, get_settings


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    settings = get_settings()
    tts_service = get_tts_service()

    return HealthResponse(
        status="healthy",
        model_loaded=tts_service.is_loaded,
        model_id=settings.model_id,
    )
