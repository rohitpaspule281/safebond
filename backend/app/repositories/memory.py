from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.memory_chunk import MemoryChunk


class MemoryChunkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_many(self, chunks: list[MemoryChunk]) -> list[MemoryChunk]:
        self.session.add_all(chunks)
        await self.session.flush()
        return chunks

    async def list_for_conversation(self, conversation_id: str, user_id: str) -> list[MemoryChunk]:
        statement = (
            select(MemoryChunk)
            .where(MemoryChunk.conversation_id == conversation_id, MemoryChunk.user_id == user_id)
            .order_by(MemoryChunk.created_at.asc(), MemoryChunk.chunk_index.asc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def delete_for_message(self, message_id: str, user_id: str) -> None:
        statement = delete(MemoryChunk).where(
            MemoryChunk.message_id == message_id,
            MemoryChunk.user_id == user_id,
        )
        await self.session.execute(statement)
