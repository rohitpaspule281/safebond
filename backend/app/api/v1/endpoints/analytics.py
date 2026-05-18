from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.session import get_db_session
from app.schemas.analytics import DashboardAnalyticsResponse, InsightsAnalyticsResponse
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardAnalyticsResponse)
async def get_dashboard_analytics(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DashboardAnalyticsResponse:
    service = AnalyticsService(session)
    return await service.dashboard(user_id=current_user.id)


@router.get("/insights", response_model=InsightsAnalyticsResponse)
async def get_insights_analytics(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> InsightsAnalyticsResponse:
    service = AnalyticsService(session)
    return await service.insights(user_id=current_user.id)
