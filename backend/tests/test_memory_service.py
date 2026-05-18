from datetime import UTC, datetime, timedelta

import pytest

from app.schemas.conversation import MessageCreateRequest
from app.schemas.memory import ContextRetrieveRequest, MemorySearchRequest
from app.services import memory as memory_service_module
from app.services.rag import RAGContextService


class FakeEmbeddingModel:
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class FakeSession:
    async def commit(self) -> None:
        return None

    async def flush(self) -> None:
        return None

    async def refresh(self, _obj) -> None:
        return None

    def add(self, _obj) -> None:
        return None

    def add_all(self, _objs) -> None:
        return None


def _fake_raw_result(now: datetime) -> dict:
    old = (now - timedelta(days=20)).timestamp()
    recent = (now - timedelta(hours=2)).timestamp()
    return {
        "ids": [["m1", "m2"]],
        "documents": [[
            "I have been overwhelmed by deadlines and pressure at work.",
            "I felt a little down a few weeks ago.",
        ]],
        "metadatas": [[
            {
                "message_id": "msg1",
                "conversation_id": "conv-1",
                "role": "user",
                "importance_score": 0.92,
                "created_at_ts": recent,
            },
            {
                "message_id": "msg2",
                "conversation_id": "conv-2",
                "role": "user",
                "importance_score": 0.42,
                "created_at_ts": old,
            },
        ]],
        "distances": [[0.08, 0.12]],
    }


@pytest.mark.asyncio
async def test_memory_chunking_and_context_ranking(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(memory_service_module, "get_memory_embedding_model", lambda: FakeEmbeddingModel())
    monkeypatch.setattr(
        memory_service_module,
        "query_memory_documents",
        lambda **kwargs: _fake_raw_result(datetime.now(UTC)),
    )

    service = memory_service_module.ConversationalMemoryService(FakeSession())
    chunks = service._chunk_message(
        "I have been very stressed about exams. I cannot keep up with the pressure. "
        "It feels like everything is piling up at once."
    )
    assert len(chunks) >= 1
    assert chunks[0].importance_score >= 0.35

    response = await service.search_memories(
        user_id="user-1",
        payload=MemorySearchRequest(query="I am stressed about work", conversation_id="conv-1", top_k=2),
    )
    assert response.results[0].conversation_id == "conv-1"
    assert response.results[0].final_score >= response.results[1].final_score


@pytest.mark.asyncio
async def test_rag_context_injection_contains_memory_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(memory_service_module, "get_memory_embedding_model", lambda: FakeEmbeddingModel())
    monkeypatch.setattr(
        memory_service_module,
        "query_memory_documents",
        lambda **kwargs: _fake_raw_result(datetime.now(UTC)),
    )

    service = RAGContextService(FakeSession())
    response = await service.build_context(
        user_id="user-1",
        payload=ContextRetrieveRequest(query="Help me continue this conversation", conversation_id="conv-1"),
    )
    assert "Memory 1" in response.injected_context
    assert len(response.retrieved_memories) >= 1
