from datetime import datetime

from pydantic import BaseModel, Field


class MemorySearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)


class RetrievedMemoryResponse(BaseModel):
    memory_id: str
    message_id: str
    conversation_id: str
    role: str
    content: str
    semantic_score: float
    recency_score: float
    importance_score: float
    same_conversation_boost: float
    final_score: float
    created_at: datetime | None = None


class MemorySearchResponse(BaseModel):
    query: str
    results: list[RetrievedMemoryResponse]


class MemoryChunkResponse(BaseModel):
    id: str
    conversation_id: str
    message_id: str
    role: str
    content: str
    chunk_index: int
    token_estimate: int
    importance_score: float
    created_at: datetime


class MemoryChunkListResponse(BaseModel):
    conversation_id: str
    chunks: list[MemoryChunkResponse]


class ContextRetrieveRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)


class ContextRetrieveResponse(BaseModel):
    query: str
    conversation_id: str | None = None
    retrieved_memories: list[RetrievedMemoryResponse]
    injected_context: str
    retrieval_summary: str
