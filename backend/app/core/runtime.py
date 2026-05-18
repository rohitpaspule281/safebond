from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RuntimeComponentSnapshot:
    name: str
    status: str
    detail: str
    warmed_at: str | None = None


_STATE_LOCK = threading.Lock()
_WARMUP_STARTED = threading.Event()
_RUNTIME_STATE: dict[str, RuntimeComponentSnapshot] = {
    "safety_classifier": RuntimeComponentSnapshot(
        name="safety_classifier",
        status="pending",
        detail="Safety classifier is waiting to warm.",
    ),
    "emotion_classifier": RuntimeComponentSnapshot(
        name="emotion_classifier",
        status="pending",
        detail="Emotion classifier is waiting to warm.",
    ),
    "sentiment_classifier": RuntimeComponentSnapshot(
        name="sentiment_classifier",
        status="pending",
        detail="Sentiment classifier is waiting to warm.",
    ),
    "memory_embeddings": RuntimeComponentSnapshot(
        name="memory_embeddings",
        status="pending",
        detail="Embedding model is waiting to warm.",
    ),
}


def get_runtime_component_statuses() -> list[RuntimeComponentSnapshot]:
    with _STATE_LOCK:
        return [
            RuntimeComponentSnapshot(
                name=item.name,
                status=item.status,
                detail=item.detail,
                warmed_at=item.warmed_at,
            )
            for item in _RUNTIME_STATE.values()
        ]


def start_background_model_warmup() -> None:
    settings = get_settings()
    if not settings.model_warmup_on_startup or _WARMUP_STARTED.is_set():
        return

    _WARMUP_STARTED.set()
    thread = threading.Thread(
        target=_warmup_worker,
        name="safebond-model-warmup",
        daemon=True,
    )
    thread.start()
    logger.info("model_warmup_started")


def _warmup_worker() -> None:
    from app.integrations.huggingface_emotion import get_emotion_classifier, get_sentiment_classifier
    from app.integrations.huggingface_safety import get_safety_zero_shot_classifier
    from app.integrations.sentence_transformer_embeddings import get_memory_embedding_model

    _warm_component(
        "safety_classifier",
        "Warming the safety classifier for first-response safety routing.",
        get_safety_zero_shot_classifier().warmup,
    )
    _warm_component(
        "emotion_classifier",
        "Warming the emotion classifier for first-response emotion analysis.",
        get_emotion_classifier().warmup,
    )
    _warm_component(
        "sentiment_classifier",
        "Warming the sentiment classifier for confidence calibration.",
        get_sentiment_classifier().warmup,
    )
    _warm_component(
        "memory_embeddings",
        "Warming the embedding model for conversational memory retrieval.",
        get_memory_embedding_model().warmup,
    )


def _warm_component(name: str, detail: str, action: Callable[[], None]) -> None:
    _update_state(name, status="warming", detail=detail)
    started_at = time.perf_counter()
    try:
        action()
    except Exception as exc:
        logger.exception("model_warmup_failed", extra={"component": name}, exc_info=exc)
        _update_state(
            name,
            status="error",
            detail=f"Warmup failed: {exc}",
        )
        return

    runtime_ms = round((time.perf_counter() - started_at) * 1000, 2)
    _update_state(
        name,
        status="ready",
        detail=f"Warmup complete in {runtime_ms} ms.",
        warmed_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    logger.info("model_warmup_completed", extra={"component": name, "runtime_ms": runtime_ms})


def _update_state(name: str, *, status: str, detail: str, warmed_at: str | None = None) -> None:
    with _STATE_LOCK:
        previous = _RUNTIME_STATE[name]
        _RUNTIME_STATE[name] = RuntimeComponentSnapshot(
            name=name,
            status=status,
            detail=detail,
            warmed_at=warmed_at if warmed_at is not None else previous.warmed_at,
        )
