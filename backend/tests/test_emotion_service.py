import pytest

from app.core.cache import TTLCache
from app.integrations.huggingface_emotion import ClassificationResult, LabelScore
from app.schemas.emotion import EmotionAnalysisRequest
from app.services import emotion as emotion_service_module


class FakeClassifier:
    def __init__(self, labels: list[LabelScore], *, model_name: str) -> None:
        self.labels = labels
        self.model_name = model_name

    def predict(self, text: str, *, top_k: int = 3) -> ClassificationResult:
        return ClassificationResult(
            labels=self.labels[:top_k],
            model_name=self.model_name,
            device="cpu",
            runtime_ms=1.25,
        )

    def predict_many(self, texts: list[str], *, top_k: int = 3) -> list[ClassificationResult]:
        return [self.predict(text, top_k=top_k) for text in texts]

    def metadata(self) -> dict[str, str | int | bool]:
        return {
            "model_name": self.model_name,
            "max_length": 256,
            "device": "cpu",
            "loaded": True,
        }


@pytest.mark.asyncio
async def test_emotion_service_maps_fear_and_cues_to_anxiety(monkeypatch: pytest.MonkeyPatch) -> None:
    emotion_classifier = FakeClassifier(
        [
            LabelScore(label="fear", score=0.74),
            LabelScore(label="sadness", score=0.11),
            LabelScore(label="anger", score=0.05),
            LabelScore(label="neutral", score=0.04),
            LabelScore(label="surprise", score=0.03),
            LabelScore(label="joy", score=0.02),
            LabelScore(label="disgust", score=0.01),
        ],
        model_name="fake-emotion-model",
    )
    sentiment_classifier = FakeClassifier(
        [
            LabelScore(label="negative", score=0.82),
            LabelScore(label="neutral", score=0.12),
            LabelScore(label="positive", score=0.06),
        ],
        model_name="fake-sentiment-model",
    )

    monkeypatch.setattr(emotion_service_module, "get_emotion_classifier", lambda: emotion_classifier)
    monkeypatch.setattr(emotion_service_module, "get_sentiment_classifier", lambda: sentiment_classifier)
    monkeypatch.setattr(
        emotion_service_module,
        "get_emotion_analysis_cache",
        lambda: TTLCache(max_size=16, ttl_seconds=60),
    )

    service = emotion_service_module.EmotionAnalysisService()
    response = await service.analyze(
        EmotionAnalysisRequest(text="I am overthinking, scared, and I can't relax at all.")
    )

    assert response.primary_emotion == "anxiety"
    assert response.confidence > 0.5
    assert response.explanation is not None
    assert "scared" in " ".join(response.explanation.lexical_cues)


@pytest.mark.asyncio
async def test_emotion_service_returns_cached_result_on_repeat(monkeypatch: pytest.MonkeyPatch) -> None:
    emotion_classifier = FakeClassifier(
        [
            LabelScore(label="sadness", score=0.68),
            LabelScore(label="fear", score=0.16),
            LabelScore(label="anger", score=0.08),
            LabelScore(label="neutral", score=0.05),
            LabelScore(label="joy", score=0.02),
            LabelScore(label="surprise", score=0.01),
        ],
        model_name="fake-emotion-model",
    )
    sentiment_classifier = FakeClassifier(
        [
            LabelScore(label="negative", score=0.79),
            LabelScore(label="neutral", score=0.15),
            LabelScore(label="positive", score=0.06),
        ],
        model_name="fake-sentiment-model",
    )

    monkeypatch.setattr(emotion_service_module, "get_emotion_classifier", lambda: emotion_classifier)
    monkeypatch.setattr(emotion_service_module, "get_sentiment_classifier", lambda: sentiment_classifier)
    monkeypatch.setattr(
        emotion_service_module,
        "get_emotion_analysis_cache",
        lambda: TTLCache(max_size=16, ttl_seconds=60),
    )

    service = emotion_service_module.EmotionAnalysisService()
    first = await service.analyze(EmotionAnalysisRequest(text="I feel lonely and down today."))
    second = await service.analyze(EmotionAnalysisRequest(text="I feel lonely and down today."))

    assert first.cached is False
    assert second.cached is True
