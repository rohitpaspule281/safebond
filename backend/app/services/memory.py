from __future__ import annotations

import asyncio
import logging
import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import NotFoundException
from app.db.models.memory_chunk import MemoryChunk
from app.integrations.chroma import query_memory_documents, upsert_memory_documents
from app.integrations.sentence_transformer_embeddings import get_memory_embedding_model
from app.repositories.conversation import ConversationRepository
from app.repositories.memory import MemoryChunkRepository
from app.repositories.message import MessageRepository
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
    MessageCreateRequest,
    MessageListResponse,
    MessageResponse,
)
from app.schemas.memory import (
    MemoryChunkListResponse,
    MemoryChunkResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    RetrievedMemoryResponse,
)

logger = logging.getLogger(__name__)

_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+|\n+")
_MULTISPACE_PATTERN = re.compile(r"\s+")


@dataclass(slots=True)
class MemoryChunkDraft:
    chunk_index: int
    content: str
    token_estimate: int
    importance_score: float


class ConversationalMemoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()
        self.conversations = ConversationRepository(session)
        self.messages = MessageRepository(session)
        self.memory_chunks = MemoryChunkRepository(session)
        self.embedding_model = get_memory_embedding_model()

    async def create_conversation(
        self,
        *,
        user_id: str,
        payload: ConversationCreateRequest,
    ) -> ConversationResponse:
        title = payload.title or "New reflection"
        conversation = await self.conversations.create(
            user_id=user_id,
            title=title,
            summary=payload.summary,
        )
        await self.session.commit()
        return ConversationResponse.model_validate(conversation)

    async def list_conversations(self, *, user_id: str) -> ConversationListResponse:
        conversations = await self.conversations.list_for_user(user_id)
        return ConversationListResponse(
            conversations=[ConversationResponse.model_validate(item) for item in conversations]
        )

    async def get_conversation_detail(
        self,
        *,
        user_id: str,
        conversation_id: str,
    ) -> ConversationDetailResponse:
        conversation = await self.conversations.get_for_user(conversation_id, user_id)
        if conversation is None:
            raise NotFoundException(detail="Conversation not found.")

        return ConversationDetailResponse(
            conversation=ConversationResponse.model_validate(conversation),
            messages=[MessageResponse.model_validate(message) for message in conversation.messages],
        )

    async def add_message(
        self,
        *,
        user_id: str,
        conversation_id: str,
        payload: MessageCreateRequest,
    ) -> MessageResponse:
        conversation = await self.conversations.get_for_user(conversation_id, user_id)
        if conversation is None:
            raise NotFoundException(detail="Conversation not found.")

        message = await self.messages.create(
            conversation_id=conversation.id,
            user_id=user_id,
            role=payload.role,
            content=self._normalize_text(payload.content),
        )

        now = datetime.now(UTC)
        conversation.last_message_at = now
        conversation.updated_at = now
        if conversation.title == "New reflection" and payload.role == "user":
            conversation.title = self._derive_conversation_title(payload.content)

        should_index = payload.index_for_memory
        if should_index is None:
            should_index = payload.role in {"user", "assistant"} and self.settings.memory_index_assistant_messages
        if payload.role == "user":
            should_index = True

        if should_index:
            await self._index_message_memory(
                user_id=user_id,
                conversation_id=conversation.id,
                message_id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at or now,
            )

        await self.session.commit()
        return MessageResponse.model_validate(message)

    async def list_messages(
        self,
        *,
        user_id: str,
        conversation_id: str,
    ) -> MessageListResponse:
        conversation = await self.conversations.get_for_user(conversation_id, user_id)
        if conversation is None:
            raise NotFoundException(detail="Conversation not found.")

        messages = await self.messages.list_for_conversation(conversation_id, user_id)
        return MessageListResponse(
            conversation_id=conversation_id,
            messages=[MessageResponse.model_validate(message) for message in messages],
        )

    async def list_memory_chunks(
        self,
        *,
        user_id: str,
        conversation_id: str,
    ) -> MemoryChunkListResponse:
        conversation = await self.conversations.get_for_user(conversation_id, user_id)
        if conversation is None:
            raise NotFoundException(detail="Conversation not found.")

        chunks = await self.memory_chunks.list_for_conversation(conversation_id, user_id)
        return MemoryChunkListResponse(
            conversation_id=conversation_id,
            chunks=[
                MemoryChunkResponse(
                    id=chunk.id,
                    conversation_id=chunk.conversation_id,
                    message_id=chunk.message_id,
                    role=chunk.role,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    token_estimate=chunk.token_estimate,
                    importance_score=round(chunk.importance_score, 4),
                    created_at=chunk.created_at,
                )
                for chunk in chunks
            ],
        )

    async def search_memories(
        self,
        *,
        user_id: str,
        payload: MemorySearchRequest,
        exclude_message_ids: list[str] | None = None,
    ) -> MemorySearchResponse:
        query_embedding = await asyncio.to_thread(
            self.embedding_model.embed_query,
            self._normalize_text(payload.query),
        )
        raw_result = await asyncio.to_thread(
            query_memory_documents,
            query_embedding=query_embedding,
            top_k=max(payload.top_k * self.settings.memory_candidate_multiplier, payload.top_k),
            where={"user_id": user_id},
        )
        ranked = self._rank_retrieved_memories(
            raw_result=raw_result,
            target_conversation_id=payload.conversation_id,
            top_k=payload.top_k,
            exclude_message_ids=set(exclude_message_ids or []),
        )
        return MemorySearchResponse(query=payload.query, results=ranked)

    async def _index_message_memory(
        self,
        *,
        user_id: str,
        conversation_id: str,
        message_id: str,
        role: str,
        content: str,
        created_at: datetime,
    ) -> None:
        drafts = self._chunk_message(content)
        if not drafts:
            return

        embeddings = await asyncio.to_thread(
            self.embedding_model.embed_documents,
            [draft.content for draft in drafts],
        )

        chunk_models: list[MemoryChunk] = []
        metadatas: list[dict[str, str | int | float | bool]] = []
        ids: list[str] = []
        documents: list[str] = []
        created_timestamp = created_at.timestamp()

        for draft in drafts:
            chunk = MemoryChunk(
                user_id=user_id,
                conversation_id=conversation_id,
                message_id=message_id,
                role=role,
                chunk_index=draft.chunk_index,
                content=draft.content,
                token_estimate=draft.token_estimate,
                importance_score=draft.importance_score,
            )
            chunk_models.append(chunk)

        await self.memory_chunks.create_many(chunk_models)

        for draft, chunk in zip(drafts, chunk_models, strict=False):
            ids.append(chunk.id)
            documents.append(chunk.content)
            metadatas.append(
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "message_id": message_id,
                    "role": role,
                    "chunk_index": draft.chunk_index,
                    "importance_score": round(draft.importance_score, 6),
                    "created_at_ts": created_timestamp,
                    "token_estimate": draft.token_estimate,
                }
            )

        await asyncio.to_thread(
            upsert_memory_documents,
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        logger.info(
            "memory_indexed",
            extra={
                "conversation_id": conversation_id,
                "message_id": message_id,
                "chunk_count": len(drafts),
            },
        )

    def _chunk_message(self, content: str) -> list[MemoryChunkDraft]:
        normalized = self._normalize_text(content)
        if not normalized:
            return []

        units = [unit.strip() for unit in _SENTENCE_SPLIT_PATTERN.split(normalized) if unit.strip()]
        if not units:
            units = [normalized]

        drafts: list[MemoryChunkDraft] = []
        current: list[str] = []
        current_char_count = 0
        overlap_units = self.settings.memory_chunk_overlap_sentences

        for unit in units:
            unit_length = len(unit)
            projected = current_char_count + unit_length + (1 if current else 0)
            if current and projected > self.settings.memory_chunk_size_chars:
                chunk_text = " ".join(current).strip()
                drafts.append(self._build_chunk_draft(len(drafts), chunk_text))
                current = current[-overlap_units:] if overlap_units > 0 else []
                current_char_count = len(" ".join(current))

            current.append(unit)
            current_char_count = len(" ".join(current))

        if current:
            drafts.append(self._build_chunk_draft(len(drafts), " ".join(current).strip()))

        return drafts

    def _build_chunk_draft(self, chunk_index: int, text: str) -> MemoryChunkDraft:
        token_estimate = max(1, math.ceil(len(text.split()) * 1.25))
        importance_score = self._calculate_importance_score(text)
        return MemoryChunkDraft(
            chunk_index=chunk_index,
            content=text,
            token_estimate=token_estimate,
            importance_score=importance_score,
        )

    def _calculate_importance_score(self, text: str) -> float:
        lowered = text.lower()
        first_person_markers = sum(lowered.count(token) for token in (" i ", " my ", " me ", " myself "))
        emotion_markers = sum(
            lowered.count(token)
            for token in ("feel", "felt", "anxious", "sad", "lonely", "stressed", "angry")
        )
        reflection_markers = sum(
            lowered.count(token)
            for token in ("because", "remember", "always", "never", "important", "struggling")
        )
        score = 0.35 + min(first_person_markers, 4) * 0.08 + min(emotion_markers, 4) * 0.08 + min(reflection_markers, 3) * 0.07
        return round(min(score, 0.98), 4)

    def _rank_retrieved_memories(
        self,
        *,
        raw_result: dict,
        target_conversation_id: str | None,
        top_k: int,
        exclude_message_ids: set[str],
    ) -> list[RetrievedMemoryResponse]:
        documents = raw_result.get("documents", [[]])[0]
        metadatas = raw_result.get("metadatas", [[]])[0]
        distances = raw_result.get("distances", [[]])[0]
        ids = raw_result.get("ids", [[]])[0]

        now_ts = datetime.now(UTC).timestamp()
        ranked: list[RetrievedMemoryResponse] = []

        for memory_id, document, metadata, distance in zip(ids, documents, metadatas, distances, strict=False):
            if str(metadata.get("message_id")) in exclude_message_ids:
                continue
            semantic_score = self._semantic_score(distance)
            recency_score = self._recency_score(float(metadata.get("created_at_ts", now_ts)), now_ts)
            importance_score = float(metadata.get("importance_score", 0.5))
            same_conversation_boost = (
                self.settings.memory_same_conversation_boost
                if target_conversation_id and metadata.get("conversation_id") == target_conversation_id
                else 0.0
            )
            final_score = min(
                1.0,
                semantic_score * self.settings.memory_semantic_weight
                + recency_score * self.settings.memory_recency_weight
                + importance_score * self.settings.memory_importance_weight
                + same_conversation_boost,
            )
            ranked.append(
                RetrievedMemoryResponse(
                    memory_id=str(memory_id),
                    message_id=str(metadata.get("message_id")),
                    conversation_id=str(metadata.get("conversation_id")),
                    role=str(metadata.get("role")),
                    content=str(document),
                    semantic_score=round(semantic_score, 4),
                    recency_score=round(recency_score, 4),
                    importance_score=round(importance_score, 4),
                    same_conversation_boost=round(same_conversation_boost, 4),
                    final_score=round(final_score, 4),
                    created_at=datetime.fromtimestamp(
                        float(metadata.get("created_at_ts", now_ts)),
                        tz=UTC,
                    ),
                )
            )

        ranked.sort(key=lambda item: item.final_score, reverse=True)
        return ranked[:top_k]

    def _semantic_score(self, distance: float) -> float:
        return max(0.0, min(1.0, 1.0 - float(distance)))

    def _recency_score(self, created_ts: float, now_ts: float) -> float:
        age_hours = max(0.0, (now_ts - created_ts) / 3600)
        half_life = max(1.0, float(self.settings.memory_recency_half_life_hours))
        return pow(0.5, age_hours / half_life)

    def _derive_conversation_title(self, content: str) -> str:
        cleaned = self._normalize_text(content)
        snippet = cleaned[:48].strip()
        return snippet if len(cleaned) <= 48 else f"{snippet}..."

    def _normalize_text(self, text: str) -> str:
        return _MULTISPACE_PATTERN.sub(" ", text.strip())[: self.settings.memory_text_hard_limit]
