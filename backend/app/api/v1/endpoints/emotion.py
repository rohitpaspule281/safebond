from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.models.user import User
from app.schemas.emotion import (
    BatchEmotionAnalysisRequest,
    BatchEmotionAnalysisResponse,
    EmotionAnalysisRequest,
    EmotionAnalysisResponse,
    EmotionModelCatalogResponse,
)
from app.services.emotion import EmotionAnalysisService

router = APIRouter(prefix="/emotions", tags=["emotions"])


@router.post("/analyze", response_model=EmotionAnalysisResponse)
async def analyze_emotion(
    payload: EmotionAnalysisRequest,
    _: Annotated[User, Depends(get_current_user)],
) -> EmotionAnalysisResponse:
    service = EmotionAnalysisService()
    return await service.analyze(payload)


@router.post("/batch-analyze", response_model=BatchEmotionAnalysisResponse)
async def batch_analyze_emotions(
    payload: BatchEmotionAnalysisRequest,
    _: Annotated[User, Depends(get_current_user)],
) -> BatchEmotionAnalysisResponse:
    service = EmotionAnalysisService()
    return await service.batch_analyze(payload)


@router.get("/models", response_model=EmotionModelCatalogResponse)
async def get_emotion_models(
    _: Annotated[User, Depends(get_current_user)],
) -> EmotionModelCatalogResponse:
    service = EmotionAnalysisService()
    return service.get_model_catalog()
