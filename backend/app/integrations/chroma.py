from functools import lru_cache
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_chroma_client():
    settings = get_settings()
    if settings.chroma_mode == "http":
        return chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
            ssl=settings.chroma_ssl,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

    return chromadb.PersistentClient(
        path=settings.chroma_persist_directory,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def check_chroma_connection() -> bool:
    client = get_chroma_client()
    client.heartbeat()
    return True


def get_memory_collection_name() -> str:
    settings = get_settings()
    return f"{settings.chroma_collection_prefix}_memory"


def get_or_create_memory_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=get_memory_collection_name(),
        metadata={"hnsw:space": "cosine"},
    )


def upsert_memory_documents(
    *,
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict[str, Any]],
) -> None:
    collection = get_or_create_memory_collection()
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def query_memory_documents(
    *,
    query_embedding: list[float],
    top_k: int,
    where: dict[str, Any] | None = None,
) -> dict[str, Any]:
    collection = get_or_create_memory_collection()
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
