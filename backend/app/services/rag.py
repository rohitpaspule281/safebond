from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.memory import ContextRetrieveRequest, ContextRetrieveResponse, MemorySearchRequest
from app.services.memory import ConversationalMemoryService


class RAGContextService:
    def __init__(self, session: AsyncSession) -> None:
        self.memory_service = ConversationalMemoryService(session)

    async def build_context(
        self,
        *,
        user_id: str,
        payload: ContextRetrieveRequest,
        exclude_message_ids: list[str] | None = None,
    ) -> ContextRetrieveResponse:
        search_response = await self.memory_service.search_memories(
            user_id=user_id,
            payload=MemorySearchRequest(
                query=payload.query,
                conversation_id=payload.conversation_id,
                top_k=payload.top_k,
            ),
            exclude_message_ids=exclude_message_ids,
        )

        injected_lines = [
            "Use the following personalized memory context to preserve continuity and empathy.",
        ]
        for index, item in enumerate(search_response.results, start=1):
            injected_lines.append(
                f"[Memory {index}] role={item.role} conversation={item.conversation_id} "
                f"score={item.final_score:.2f}: {item.content}"
            )

        retrieval_summary = (
            f"Retrieved {len(search_response.results)} memory snippets ranked by semantic similarity, "
            "recency, importance, and same-conversation boost."
        )
        return ContextRetrieveResponse(
            query=payload.query,
            conversation_id=payload.conversation_id,
            retrieved_memories=search_response.results,
            injected_context="\n".join(injected_lines),
            retrieval_summary=retrieval_summary,
        )
