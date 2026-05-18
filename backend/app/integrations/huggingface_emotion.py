from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LabelScore:
    label: str
    score: float


@dataclass(slots=True)
class ClassificationResult:
    labels: list[LabelScore]
    model_name: str
    device: str
    runtime_ms: float


class HuggingFaceSequenceClassifier:
    def __init__(self, *, model_name: str, max_length: int) -> None:
        self.model_name = model_name
        self.max_length = max_length
        self._load_lock = threading.Lock()
        self._model: Any | None = None
        self._tokenizer: Any | None = None
        self._torch: Any | None = None
        self._device: Any | None = None
        self._device_label = "uninitialized"

    def predict(self, text: str, *, top_k: int = 3) -> ClassificationResult:
        return self.predict_many([text], top_k=top_k)[0]

    def predict_many(self, texts: list[str], *, top_k: int = 3) -> list[ClassificationResult]:
        self._ensure_loaded()
        assert self._torch is not None
        assert self._model is not None
        assert self._tokenizer is not None
        assert self._device is not None

        started_at = time.perf_counter()
        encoded = self._tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        encoded = {key: value.to(self._device) for key, value in encoded.items()}

        with self._torch.inference_mode():
            outputs = self._model(**encoded)
            probabilities = self._torch.softmax(outputs.logits, dim=-1).detach().cpu().tolist()

        runtime_ms = round((time.perf_counter() - started_at) * 1000, 2)
        labels = [self._normalize_label(self._model.config.id2label[idx]) for idx in range(len(probabilities[0]))]

        results: list[ClassificationResult] = []
        for scores in probabilities:
            ranked = sorted(
                [LabelScore(label=labels[idx], score=round(float(score), 6)) for idx, score in enumerate(scores)],
                key=lambda item: item.score,
                reverse=True,
            )[:top_k]
            results.append(
                ClassificationResult(
                    labels=ranked,
                    model_name=self.model_name,
                    device=self._device_label,
                    runtime_ms=runtime_ms,
                )
            )
        return results

    def warmup(self) -> None:
        self.predict("Warmup request for Safebond.")

    def metadata(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "max_length": self.max_length,
            "device": self._device_label,
            "loaded": self._model is not None,
        }

    def _ensure_loaded(self) -> None:
        if self._model is not None and self._tokenizer is not None and self._torch is not None:
            return

        with self._load_lock:
            if self._model is not None and self._tokenizer is not None and self._torch is not None:
                return

            self._load_runtime()

    def _load_runtime(self) -> None:
        settings = get_settings()
        transformers = __import__("transformers", fromlist=["AutoModelForSequenceClassification"])
        torch = __import__("torch")

        preferred_device = self._resolve_device(torch, settings.emotion_device_preference)
        tokenizer = transformers.AutoTokenizer.from_pretrained(
            self.model_name,
            local_files_only=settings.hf_local_files_only,
        )
        model = transformers.AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            local_files_only=settings.hf_local_files_only,
        )
        model.eval()

        try:
            model.to(preferred_device)
            self._device = preferred_device
            self._device_label = str(preferred_device)
        except Exception as exc:
            if str(preferred_device) != "cpu":
                logger.warning(
                    "model_device_fallback",
                    extra={"model_name": self.model_name, "preferred_device": str(preferred_device)},
                )
                model.to(torch.device("cpu"))
                self._device = torch.device("cpu")
                self._device_label = "cpu"
            else:
                raise exc

        if settings.torch_num_threads:
            torch.set_num_threads(settings.torch_num_threads)

        self._model = model
        self._tokenizer = tokenizer
        self._torch = torch
        logger.info(
            "transformer_model_loaded",
            extra={"model_name": self.model_name, "device": self._device_label},
        )

    def _normalize_label(self, label: str) -> str:
        normalized = label.lower()
        cardiff_mapping = {
            "label_0": "negative",
            "label_1": "neutral",
            "label_2": "positive",
        }
        return cardiff_mapping.get(normalized, normalized)

    def _resolve_device(self, torch: Any, preference: str):
        if preference == "cpu":
            return torch.device("cpu")
        if preference == "cuda":
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA device preference was set, but CUDA is unavailable.")
            return torch.device("cuda")
        if torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")


@lru_cache(maxsize=1)
def get_emotion_classifier() -> HuggingFaceSequenceClassifier:
    settings = get_settings()
    return HuggingFaceSequenceClassifier(
        model_name=settings.emotion_model_name,
        max_length=settings.emotion_max_length,
    )


@lru_cache(maxsize=1)
def get_sentiment_classifier() -> HuggingFaceSequenceClassifier:
    settings = get_settings()
    return HuggingFaceSequenceClassifier(
        model_name=settings.sentiment_model_name,
        max_length=settings.sentiment_max_length,
    )
