from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.session import get_db_session
from app.schemas.memory import (
    ContextRetrieveRequest,
    ContextRetrieveResponse,
    MemoryChunkListResponse,
    MemorySearchRequest,
    MemorySearchResponse,
)
from app.services.memory import ConversationalMemoryService
from app.services.rag import RAGContextService

router = APIRouter(tags=["memory", "rag"])


@router.post("/memory/search", response_model=MemorySearchResponse)
async def search_memories(
    payload: MemorySearchRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MemorySearchResponse:
    service = ConversationalMemoryService(session)
    return await service.search_memories(user_id=current_user.id, payload=payload)


@router.get("/memory/conversations/{conversation_id}/chunks", response_model=MemoryChunkListResponse)
async def list_memory_chunks(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MemoryChunkListResponse:
    service = ConversationalMemoryService(session)
    return await service.list_memory_chunks(
        user_id=current_user.id,
        conversation_id=conversation_id,
    )


@router.post("/rag/context", response_model=ContextRetrieveResponse)
async def build_rag_context(
    payload: ContextRetrieveRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ContextRetrieveResponse:
    service = RAGContextService(session)
    return await service.build_context(user_id=current_user.id, payload=payload)
