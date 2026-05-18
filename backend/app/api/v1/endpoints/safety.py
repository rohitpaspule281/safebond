from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.models.user import User
from app.schemas.safety import (
    ResponseModerationRequest,
    ResponseModerationResponse,
    SafetyAssessmentResponse,
    SafetyEvaluateRequest,
    SafetyResourceCatalogResponse,
)
from app.services.safety import SafetyRiskService

router = APIRouter(prefix="/safety", tags=["safety"])


@router.post("/evaluate", response_model=SafetyAssessmentResponse)
async def evaluate_safety(
    payload: SafetyEvaluateRequest,
    _: Annotated[User, Depends(get_current_user)],
) -> SafetyAssessmentResponse:
    service = SafetyRiskService()
    return await service.evaluate(payload)


@router.post("/moderate-response", response_model=ResponseModerationResponse)
async def moderate_response(
    payload: ResponseModerationRequest,
    _: Annotated[User, Depends(get_current_user)],
) -> ResponseModerationResponse:
    service = SafetyRiskService()
    return await service.moderate_response(payload)


@router.get("/resources", response_model=SafetyResourceCatalogResponse)
async def get_safety_resources(
    _: Annotated[User, Depends(get_current_user)],
) -> SafetyResourceCatalogResponse:
    service = SafetyRiskService()
    return service.get_resources()
