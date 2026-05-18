from http import HTTPStatus

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.health import HealthResponse, LivenessResponse
from app.services.health import HealthService

router = APIRouter(tags=["health"])

health_service = HealthService()


@router.get("/health/live", response_model=LivenessResponse)
async def health_liveness() -> LivenessResponse:
    return await health_service.liveness()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return await health_service.readiness()


@router.get("/health/ready", response_model=HealthResponse)
async def health_readiness() -> JSONResponse | HealthResponse:
    response = await health_service.readiness()
    if response.status != "ok":
        return JSONResponse(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            content=response.model_dump(mode="json"),
        )
    return response
