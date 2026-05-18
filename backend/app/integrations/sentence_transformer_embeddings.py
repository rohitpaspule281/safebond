from __future__ import annotations

import logging
import threading
from functools import lru_cache
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class SentenceTransformerEmbeddingModel:
    def __init__(self, *, model_name: str) -> None:
        self.model_name = model_name
        self._load_lock = threading.Lock()
        self._model: Any | None = None
        self._device_label = "uninitialized"

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        model = self._ensure_loaded()
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    def metadata(self) -> dict[str, str | bool]:
        return {
            "model_name": self.model_name,
            "device": self._device_label,
            "loaded": self._model is not None,
        }

    def warmup(self) -> None:
        self.embed_query("Warmup memory embedding request.")

    def _ensure_loaded(self):
        if self._model is not None:
            return self._model

        with self._load_lock:
            if self._model is not None:
                return self._model

            settings = get_settings()
            sentence_transformers = __import__("sentence_transformers", fromlist=["SentenceTransformer"])
            torch = __import__("torch")

            device = "cpu"
            if settings.embedding_device_preference == "cuda":
                if not torch.cuda.is_available():
                    raise RuntimeError("CUDA device preference was set, but CUDA is unavailable.")
                device = "cuda"
            elif settings.embedding_device_preference == "auto" and torch.cuda.is_available():
                device = "cuda"

            model = sentence_transformers.SentenceTransformer(
                self.model_name,
                device=device,
                local_files_only=settings.hf_local_files_only,
            )
            self._model = model
            self._device_label = device
            logger.info(
                "embedding_model_loaded",
                extra={"model_name": self.model_name, "device": self._device_label},
            )
            return self._model


@lru_cache(maxsize=1)
def get_memory_embedding_model() -> SentenceTransformerEmbeddingModel:
    settings = get_settings()
    return SentenceTransformerEmbeddingModel(model_name=settings.memory_embedding_model_name)
