from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.session import get_db_session
from app.schemas.profile import (
    UserWellnessProfileEnvelopeResponse,
    UserWellnessProfileStatusResponse,
    UserWellnessProfileUpsertRequest,
)
from app.services.profile import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/status", response_model=UserWellnessProfileStatusResponse)
async def get_profile_status(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserWellnessProfileStatusResponse:
    service = ProfileService(session)
    return await service.get_status(user_id=current_user.id)


@router.get("/me", response_model=UserWellnessProfileEnvelopeResponse)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserWellnessProfileEnvelopeResponse:
    service = ProfileService(session)
    return await service.get_profile(user_id=current_user.id)


@router.put("/me", response_model=UserWellnessProfileEnvelopeResponse)
async def upsert_my_profile(
    payload: UserWellnessProfileUpsertRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserWellnessProfileEnvelopeResponse:
    service = ProfileService(session)
    return await service.upsert_profile(user_id=current_user.id, payload=payload)
