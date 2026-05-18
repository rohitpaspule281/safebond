from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.session import get_db_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatOrchestrationService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    payload: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ChatResponse:
    service = ChatOrchestrationService(session)
    return await service.handle_chat(user_id=current_user.id, payload=payload)
