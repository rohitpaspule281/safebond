from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from dataclasses import dataclass
from functools import lru_cache

from app.core.cache import TTLCache
from app.core.config import get_settings
from app.integrations.huggingface_emotion import (
    get_emotion_classifier,
    get_sentiment_classifier,
)
from app.schemas.emotion import (
    BatchEmotionAnalysisRequest,
    BatchEmotionAnalysisResponse,
    ConfidenceBreakdownResponse,
    EmotionAnalysisRequest,
    EmotionAnalysisResponse,
    EmotionModelCatalogResponse,
    EmotionModelInfoResponse,
    ExplainabilityResponse,
    HighlightedSegmentResponse,
    LabelScoreResponse,
    SentimentSummaryResponse,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CueBank:
    anxiety: tuple[str, ...] = (
        "overthinking",
        "panic",
        "worried",
        "worrying",
        "can't relax",
        "cant relax",
        "scared",
        "nervous",
        "anxious",
        "uneasy",
        "restless",
    )
    stress: tuple[str, ...] = (
        "pressure",
        "deadline",
        "too much",
        "overwhelmed",
        "stressed",
        "swamped",
        "exhausted",
        "can't keep up",
        "cant keep up",
    )
    loneliness: tuple[str, ...] = (
        "alone",
        "lonely",
        "isolated",
        "nobody",
        "no one",
        "left out",
        "disconnected",
    )
    burnout: tuple[str, ...] = (
        "burned out",
        "burnt out",
        "drained",
        "emotionally exhausted",
        "checked out",
        "empty",
        "work is killing me",
        "can't do this anymore",
        "cant do this anymore",
    )
    sadness: tuple[str, ...] = (
        "sad",
        "down",
        "hopeless",
        "crying",
        "heavy",
        "hurt",
        "depressed",
        "tired of this",
    )
    anger: tuple[str, ...] = (
        "angry",
        "frustrated",
        "annoyed",
        "furious",
        "mad",
        "irritated",
        "resent",
    )

    def as_mapping(self) -> dict[str, tuple[str, ...]]:
        return {
            "anxiety": self.anxiety,
            "stress": self.stress,
            "loneliness": self.loneliness,
            "burnout": self.burnout,
            "sadness": self.sadness,
            "anger": self.anger,
        }


_CUES = CueBank()
_CLAUSE_SPLIT_PATTERN = re.compile(r"[.!?;\n]+|(?:\s+but\s+)|(?:\s+and\s+)", re.IGNORECASE)
_MULTISPACE_PATTERN = re.compile(r"\s+")


@lru_cache(maxsize=1)
def get_emotion_analysis_cache() -> TTLCache[EmotionAnalysisResponse]:
    settings = get_settings()
    return TTLCache[EmotionAnalysisResponse](
        max_size=settings.emotion_cache_max_size,
        ttl_seconds=settings.emotion_cache_ttl_seconds,
    )


class EmotionAnalysisService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.emotion_classifier = get_emotion_classifier()
        self.sentiment_classifier = get_sentiment_classifier()
        self.cache = get_emotion_analysis_cache()

    async def analyze(self, payload: EmotionAnalysisRequest) -> EmotionAnalysisResponse:
        cache_key = self._cache_key(payload.text, payload.include_explanation, payload.top_k)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached.model_copy(update={"cached": True}, deep=True)

        result = await asyncio.to_thread(self._analyze_sync, payload.text, payload.include_explanation, payload.top_k)
        self.cache.set(cache_key, result)
        return result

    async def batch_analyze(self, payload: BatchEmotionAnalysisRequest) -> BatchEmotionAnalysisResponse:
        results: list[EmotionAnalysisResponse] = []
        for text in payload.texts:
            results.append(
                await self.analyze(
                    EmotionAnalysisRequest(
                        text=text,
                        include_explanation=payload.include_explanation,
                        top_k=payload.top_k,
                    )
                )
            )
        return BatchEmotionAnalysisResponse(results=results)

    def get_model_catalog(self) -> EmotionModelCatalogResponse:
        return EmotionModelCatalogResponse(
            models=[
                EmotionModelInfoResponse(role="emotion_classifier", **self.emotion_classifier.metadata()),
                EmotionModelInfoResponse(role="sentiment_classifier", **self.sentiment_classifier.metadata()),
            ]
        )

    def _analyze_sync(
        self,
        text: str,
        include_explanation: bool,
        top_k: int,
    ) -> EmotionAnalysisResponse:
        normalized_text = self._normalize_text(text)
        emotion_result = self.emotion_classifier.predict(normalized_text, top_k=8)
        sentiment_result = self.sentiment_classifier.predict(normalized_text, top_k=3)

        raw_emotions = {item.label: item.score for item in emotion_result.labels}
        raw_sentiments = {item.label: item.score for item in sentiment_result.labels}
        cue_scores, lexical_cues = self._lexical_cue_scores(normalized_text)
        wellness_scores = self._derive_wellness_scores(raw_emotions, raw_sentiments, cue_scores)

        top_wellness = sorted(wellness_scores.items(), key=lambda item: item[1], reverse=True)
        primary_emotion, primary_score = top_wellness[0]
        secondary_emotion = top_wellness[1][0] if len(top_wellness) > 1 else None

        label_margin = round(max(primary_score - top_wellness[1][1], 0.0), 4) if len(top_wellness) > 1 else primary_score
        sentiment_label, sentiment_score = max(raw_sentiments.items(), key=lambda item: item[1])
        sentiment_support = raw_sentiments.get("negative", 0.0) if primary_emotion != "anger" else max(
            raw_sentiments.get("negative", 0.0),
            raw_sentiments.get("neutral", 0.0) * 0.25,
        )
        cue_support = cue_scores.get(primary_emotion, 0.0)
        agreement_bonus = self._agreement_bonus(primary_emotion, raw_emotions)
        confidence = self._clamp(
            0.45 * primary_score
            + 0.20 * label_margin
            + 0.15 * sentiment_support
            + 0.10 * cue_support
            + 0.10 * agreement_bonus
        )
        emotional_intensity = self._compute_intensity(
            text=normalized_text,
            primary_score=primary_score,
            negative_sentiment=raw_sentiments.get("negative", 0.0),
            cue_support=cue_support,
        )

        top_emotions = [
            LabelScoreResponse(label=label, score=round(score, 4))
            for label, score in top_wellness[:top_k]
        ]
        sentiment_distribution = [
            LabelScoreResponse(label=label, score=round(score, 4))
            for label, score in sorted(raw_sentiments.items(), key=lambda item: item[1], reverse=True)
        ]

        explanation = None
        if include_explanation:
            highlighted_segments = self._highlight_segments(normalized_text, primary_emotion)
            explanation = ExplainabilityResponse(
                reasoning=self._build_reasoning(primary_emotion, secondary_emotion, sentiment_label),
                lexical_cues=lexical_cues[:6],
                highlighted_segments=highlighted_segments,
                model_emotions=[
                    LabelScoreResponse(label=item.label, score=round(item.score, 4))
                    for item in emotion_result.labels
                ],
                model_sentiments=[
                    LabelScoreResponse(label=item.label, score=round(item.score, 4))
                    for item in sentiment_result.labels
                ],
                confidence_breakdown=ConfidenceBreakdownResponse(
                    primary_score=round(primary_score, 4),
                    label_margin=round(label_margin, 4),
                    sentiment_support=round(sentiment_support, 4),
                    cue_support=round(cue_support, 4),
                    agreement_bonus=round(agreement_bonus, 4),
                ),
            )

        response = EmotionAnalysisResponse(
            text=text,
            primary_emotion=primary_emotion,
            secondary_emotion=secondary_emotion,
            emotional_intensity=round(emotional_intensity, 4),
            confidence=round(confidence, 4),
            top_emotions=top_emotions,
            sentiment=SentimentSummaryResponse(label=sentiment_label, score=round(sentiment_score, 4)),
            sentiment_distribution=sentiment_distribution,
            explanation=explanation,
            model_metadata=[
                EmotionModelInfoResponse(role="emotion_classifier", **self.emotion_classifier.metadata()),
                EmotionModelInfoResponse(role="sentiment_classifier", **self.sentiment_classifier.metadata()),
            ],
            cached=False,
        )
        logger.info(
            "emotion_analysis_completed",
            extra={
                "primary_emotion": primary_emotion,
                "confidence": round(confidence, 4),
                "intensity": round(emotional_intensity, 4),
            },
        )
        return response

    def _cache_key(self, text: str, include_explanation: bool, top_k: int) -> str:
        raw_key = f"{self._normalize_text(text)}|{include_explanation}|{top_k}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def _normalize_text(self, text: str) -> str:
        normalized = _MULTISPACE_PATTERN.sub(" ", text.strip())
        return normalized[: self.settings.emotion_text_hard_limit]

    def _lexical_cue_scores(self, text: str) -> tuple[dict[str, float], list[str]]:
        lowered = text.lower()
        matched_cues: list[str] = []
        cue_scores: dict[str, float] = {}
        for label, cue_set in _CUES.as_mapping().items():
            hits = [cue for cue in cue_set if cue in lowered]
            matched_cues.extend(hits)
            cue_scores[label] = self._clamp(len(hits) / max(len(cue_set) * 0.35, 1.0))
        return cue_scores, matched_cues

    def _derive_wellness_scores(
        self,
        raw_emotions: dict[str, float],
        raw_sentiments: dict[str, float],
        cue_scores: dict[str, float],
    ) -> dict[str, float]:
        fear = raw_emotions.get("fear", 0.0)
        sadness = raw_emotions.get("sadness", 0.0)
        anger = raw_emotions.get("anger", 0.0)
        neutral = raw_emotions.get("neutral", 0.0)
        negative = raw_sentiments.get("negative", 0.0)

        scores = {
            "sadness": 0.65 * sadness + 0.15 * negative + 0.20 * cue_scores.get("sadness", 0.0),
            "anxiety": 0.55 * fear + 0.20 * negative + 0.25 * cue_scores.get("anxiety", 0.0),
            "stress": 0.35 * fear
            + 0.20 * anger
            + 0.20 * sadness
            + 0.25 * cue_scores.get("stress", 0.0),
            "loneliness": 0.55 * sadness
            + 0.10 * negative
            + 0.35 * cue_scores.get("loneliness", 0.0),
            "burnout": 0.30 * sadness
            + 0.25 * anger
            + 0.15 * negative
            + 0.30 * cue_scores.get("burnout", 0.0),
            "anger": 0.70 * anger + 0.10 * negative + 0.20 * cue_scores.get("anger", 0.0),
        }
        if neutral > 0.45 and negative < 0.3:
            scores = {key: score * 0.85 for key, score in scores.items()}
        return {key: round(self._clamp(value), 6) for key, value in scores.items()}

    def _agreement_bonus(self, primary_emotion: str, raw_emotions: dict[str, float]) -> float:
        mapping = {
            "sadness": "sadness",
            "anxiety": "fear",
            "stress": "fear",
            "loneliness": "sadness",
            "burnout": "sadness",
            "anger": "anger",
        }
        source_label = mapping.get(primary_emotion)
        if source_label is None:
            return 0.0
        return raw_emotions.get(source_label, 0.0)

    def _compute_intensity(
        self,
        *,
        text: str,
        primary_score: float,
        negative_sentiment: float,
        cue_support: float,
    ) -> float:
        emphasis_score = self._emphasis_score(text)
        return self._clamp(
            0.50 * primary_score
            + 0.20 * negative_sentiment
            + 0.15 * cue_support
            + 0.15 * emphasis_score
        )

    def _emphasis_score(self, text: str) -> float:
        exclamation_weight = min(text.count("!"), 3) / 3
        question_weight = min(text.count("?"), 3) / 3
        uppercase_tokens = [token for token in text.split() if len(token) > 2 and token.isupper()]
        uppercase_weight = min(len(uppercase_tokens), 3) / 3
        elongated_words = len(re.findall(r"(\w)\1{2,}", text.lower()))
        elongated_weight = min(elongated_words, 3) / 3
        return self._clamp(
            0.35 * exclamation_weight
            + 0.20 * question_weight
            + 0.25 * uppercase_weight
            + 0.20 * elongated_weight
        )

    def _highlight_segments(self, text: str, primary_emotion: str) -> list[HighlightedSegmentResponse]:
        clauses = [segment.strip() for segment in _CLAUSE_SPLIT_PATTERN.split(text) if segment.strip()]
        if not clauses:
            return []

        selected_clauses = clauses[: self.settings.emotion_max_explanation_segments * 2]
        clause_predictions = self.emotion_classifier.predict_many(selected_clauses, top_k=3)
        mapping = {
            "sadness": ("sadness",),
            "anxiety": ("fear",),
            "stress": ("fear", "anger", "sadness"),
            "loneliness": ("sadness",),
            "burnout": ("sadness", "anger"),
            "anger": ("anger",),
        }
        supported_labels = mapping.get(primary_emotion, (primary_emotion,))

        ranked_segments: list[HighlightedSegmentResponse] = []
        for clause, prediction in zip(selected_clauses, clause_predictions, strict=False):
            clause_score = max(
                (item.score for item in prediction.labels if item.label in supported_labels),
                default=0.0,
            )
            if clause_score > 0:
                ranked_segments.append(
                    HighlightedSegmentResponse(
                        text=clause,
                        matched_emotion=primary_emotion,
                        score=round(clause_score, 4),
                    )
                )

        ranked_segments.sort(key=lambda item: item.score, reverse=True)
        return ranked_segments[: self.settings.emotion_max_explanation_segments]

    def _build_reasoning(
        self,
        primary_emotion: str,
        secondary_emotion: str | None,
        sentiment_label: str,
    ) -> str:
        if secondary_emotion:
            return (
                f"The text is primarily aligned with {primary_emotion} and secondarily with "
                f"{secondary_emotion}, with an overall {sentiment_label} sentiment profile."
            )
        return f"The text is primarily aligned with {primary_emotion} with an overall {sentiment_label} sentiment profile."

    def _clamp(self, value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, value))
