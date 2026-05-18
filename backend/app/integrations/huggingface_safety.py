from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ZeroShotLabelScore:
    label: str
    score: float


class ZeroShotSafetyClassifier:
    def __init__(self, *, model_name: str) -> None:
        self.model_name = model_name
        self._load_lock = threading.Lock()
        self._pipeline: Any | None = None
        self._device_label = "uninitialized"

    def classify(
        self,
        *,
        text: str,
        candidate_labels: list[str],
        multi_label: bool = True,
    ) -> list[ZeroShotLabelScore]:
        pipe = self._ensure_loaded()
        result = pipe(text, candidate_labels, multi_label=multi_label)
        return [
            ZeroShotLabelScore(label=str(label), score=round(float(score), 6))
            for label, score in zip(result["labels"], result["scores"], strict=False)
        ]

    def metadata(self) -> dict[str, str | bool]:
        return {
            "model_name": self.model_name,
            "device": self._device_label,
            "loaded": self._pipeline is not None,
        }

    def warmup(self) -> None:
        self.classify(
            text="I feel overwhelmed and need help.",
            candidate_labels=["severe emotional distress or panic", "request for general emotional support"],
        )

    def _ensure_loaded(self):
        if self._pipeline is not None:
            return self._pipeline

        with self._load_lock:
            if self._pipeline is not None:
                return self._pipeline

            settings = get_settings()
            transformers = __import__("transformers", fromlist=["pipeline"])
            torch = __import__("torch")

            if settings.safety_device_preference == "cuda":
                if not torch.cuda.is_available():
                    raise RuntimeError("CUDA device preference was set, but CUDA is unavailable.")
                device = 0
                self._device_label = "cuda"
            elif settings.safety_device_preference == "auto" and torch.cuda.is_available():
                device = 0
                self._device_label = "cuda"
            else:
                device = -1
                self._device_label = "cpu"

            try:
                pipe = transformers.pipeline(
                    "zero-shot-classification",
                    model=self.model_name,
                    device=device,
                    local_files_only=settings.hf_local_files_only,
                )
            except Exception:
                if device != -1:
                    logger.warning(
                        "safety_model_device_fallback",
                        extra={"model_name": self.model_name, "preferred_device": self._device_label},
                    )
                    pipe = transformers.pipeline(
                        "zero-shot-classification",
                        model=self.model_name,
                        device=-1,
                        local_files_only=settings.hf_local_files_only,
                    )
                    self._device_label = "cpu"
                else:
                    raise

            self._pipeline = pipe
            logger.info(
                "safety_zero_shot_model_loaded",
                extra={"model_name": self.model_name, "device": self._device_label},
            )
            return self._pipeline


@lru_cache(maxsize=1)
def get_safety_zero_shot_classifier() -> ZeroShotSafetyClassifier:
    settings = get_settings()
    return ZeroShotSafetyClassifier(model_name=settings.safety_zero_shot_model_name)
