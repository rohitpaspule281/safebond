from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from dataclasses import dataclass
from functools import lru_cache

from app.core.cache import TTLCache
from app.core.config import get_settings
from app.integrations.huggingface_safety import get_safety_zero_shot_classifier
from app.schemas.safety import (
    ResponseModerationRequest,
    ResponseModerationResponse,
    SafetyAssessmentResponse,
    SafetyEmergencyResourceResponse,
    SafetyEvaluateRequest,
    SafetyLexicalSignalResponse,
    SafetyModelScoreResponse,
    SafetyResourceCatalogResponse,
)

logger = logging.getLogger(__name__)

_MULTISPACE_PATTERN = re.compile(r"\s+")


@dataclass(slots=True)
class SafetyRuleBank:
    explicit_self_harm: tuple[str, ...] = (
        "kill myself",
        "end my life",
        "want to die",
        "want to disappear forever",
        "suicide",
        "take my own life",
        "hurt myself",
        "self harm",
        "self-harm",
    )
    crisis_intent: tuple[str, ...] = (
        "tonight",
        "right now",
        "cannot stay safe",
        "can't stay safe",
        "about to do it",
        "have a plan",
        "made a plan",
        "wrote a note",
        "goodbye everyone",
    )
    means_or_method: tuple[str, ...] = (
        "pills",
        "knife",
        "rope",
        "bridge",
        "poison",
        "jump off",
        "overdose",
        "blade",
        "hanging",
    )
    hopelessness: tuple[str, ...] = (
        "no reason to live",
        "everyone would be better without me",
        "nothing will get better",
        "i am a burden",
        "there is no point",
        "i can't go on",
        "cant go on",
    )
    panic_or_distress: tuple[str, ...] = (
        "panic attack",
        "can't breathe",
        "cant breathe",
        "losing control",
        "breaking down",
        "falling apart",
        "i am not safe",
    )
    violence: tuple[str, ...] = (
        "hurt them",
        "kill them",
        "attack someone",
        "make them pay",
        "violent thoughts",
    )
    unsafe_response_patterns: tuple[str, ...] = (
        "here is how to hurt yourself",
        "ways to kill yourself",
        "you should do it",
        "don't tell anyone",
        "dont tell anyone",
        "you only need me",
        "i am your therapist",
        "you definitely have",
        "just get over it",
    )

    def as_mapping(self) -> dict[str, tuple[str, ...]]:
        return {
            "explicit_self_harm": self.explicit_self_harm,
            "crisis_intent": self.crisis_intent,
            "means_or_method": self.means_or_method,
            "hopelessness": self.hopelessness,
            "panic_or_distress": self.panic_or_distress,
            "violence": self.violence,
            "unsafe_response_patterns": self.unsafe_response_patterns,
        }


_RULES = SafetyRuleBank()
_ZERO_SHOT_LABELS = [
    "self-harm or suicide risk",
    "acute crisis or imminent danger",
    "severe emotional distress or panic",
    "violence or harm to others risk",
    "request for general emotional support",
]


@lru_cache(maxsize=1)
def get_safety_cache() -> TTLCache[SafetyAssessmentResponse]:
    settings = get_settings()
    return TTLCache[SafetyAssessmentResponse](
        max_size=settings.safety_cache_max_size,
        ttl_seconds=settings.safety_cache_ttl_seconds,
    )


def get_india_emergency_resources() -> list[SafetyEmergencyResourceResponse]:
    return [
        SafetyEmergencyResourceResponse(
            name="Tele-MANAS",
            contact="14416",
            kind="mental_health",
            availability="24x7",
            region="India",
            source_name="Ministry of Health and Family Welfare",
            source_url="https://www.mohfw.gov.in/sites/default/files/Operational%20Guidelines%20-%20Tele%20Manas.pdf",
        ),
        SafetyEmergencyResourceResponse(
            name="Tele-MANAS Toll-Free",
            contact="1-800-891-4416",
            kind="mental_health",
            availability="24x7",
            region="India",
            source_name="Ministry of Health and Family Welfare",
            source_url="https://www.mohfw.gov.in/sites/default/files/Operational%20Guidelines%20-%20Tele%20Manas.pdf",
        ),
        SafetyEmergencyResourceResponse(
            name="Emergency Response Support System",
            contact="112",
            kind="emergency",
            availability="24x7",
            region="India",
            source_name="Government of India ERSS",
            source_url="https://112.gov.in/",
        ),
    ]


class SafetyRiskService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.classifier = get_safety_zero_shot_classifier()
        self.cache = get_safety_cache()

    async def evaluate(self, payload: SafetyEvaluateRequest) -> SafetyAssessmentResponse:
        cache_key = self._cache_key(payload.text, payload.include_resources)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached.model_copy(update={"cached": True}, deep=True)

        result = await asyncio.to_thread(self._evaluate_sync, payload.text, payload.include_resources)
        self.cache.set(cache_key, result)
        return result

    async def moderate_response(
        self,
        payload: ResponseModerationRequest,
    ) -> ResponseModerationResponse:
        assessment = await self.evaluate(
            SafetyEvaluateRequest(
                text=payload.user_text,
                include_resources=payload.include_resources,
            )
        )
        action_taken, blocked_flags, moderated_response = self._moderate_response_sync(
            drafted_response=payload.drafted_response,
            assessment=assessment,
        )
        return ResponseModerationResponse(
            original_response=payload.drafted_response,
            moderated_response=moderated_response,
            action_taken=action_taken,
            blocked_policy_flags=blocked_flags,
            safety_assessment=assessment,
        )

    def get_resources(self) -> SafetyResourceCatalogResponse:
        return SafetyResourceCatalogResponse(
            verified_on="2026-05-17",
            resources=get_india_emergency_resources(),
        )

    def _evaluate_sync(self, text: str, include_resources: bool) -> SafetyAssessmentResponse:
        normalized_text = self._normalize_text(text)
        zero_shot_scores = self.classifier.classify(
            text=normalized_text,
            candidate_labels=_ZERO_SHOT_LABELS,
            multi_label=True,
        )
        zero_shot_map = {item.label: item.score for item in zero_shot_scores}
        lexical_signals = self._lexical_assessment(normalized_text)
        lexical_map = {signal.category: signal.score for signal in lexical_signals}

        self_harm_score = self._clamp(
            0.65 * zero_shot_map.get("self-harm or suicide risk", 0.0)
            + 0.25 * lexical_map.get("explicit_self_harm", 0.0)
            + 0.10 * lexical_map.get("means_or_method", 0.0)
        )
        crisis_intent_score = self._clamp(
            0.50 * zero_shot_map.get("acute crisis or imminent danger", 0.0)
            + 0.25 * lexical_map.get("crisis_intent", 0.0)
            + 0.15 * lexical_map.get("means_or_method", 0.0)
            + 0.10 * lexical_map.get("hopelessness", 0.0)
        )
        distress_score = self._clamp(
            0.60 * zero_shot_map.get("severe emotional distress or panic", 0.0)
            + 0.20 * lexical_map.get("panic_or_distress", 0.0)
            + 0.20 * lexical_map.get("hopelessness", 0.0)
        )
        violence_score = self._clamp(
            0.70 * zero_shot_map.get("violence or harm to others risk", 0.0)
            + 0.30 * lexical_map.get("violence", 0.0)
        )
        risk_score = self._clamp(
            0.42 * self_harm_score
            + 0.30 * crisis_intent_score
            + 0.18 * distress_score
            + 0.10 * violence_score
        )

        has_explicit_self_harm = lexical_map.get("explicit_self_harm", 0.0) >= 0.75
        has_plan_signal = lexical_map.get("means_or_method", 0.0) >= 0.5 or lexical_map.get("crisis_intent", 0.0) >= 0.5

        risk_level = "low"
        if has_explicit_self_harm and has_plan_signal:
            risk_level = "critical"
        elif risk_score >= self.settings.safety_critical_threshold:
            risk_level = "critical"
        elif risk_score >= self.settings.safety_high_threshold or self_harm_score >= self.settings.safety_self_harm_threshold:
            risk_level = "high"
        elif risk_score >= self.settings.safety_moderate_threshold or distress_score >= 0.45:
            risk_level = "moderate"

        policy_action = {
            "low": "allow_supportive_response",
            "moderate": "support_with_safety_guidance",
            "high": "replace_with_escalation_response",
            "critical": "replace_with_emergency_crisis_response",
        }[risk_level]
        should_block_standard_response = risk_level in {"high", "critical"}
        needs_immediate_escalation = risk_level == "critical"

        reasons = self._reasons_from_scores(
            self_harm_score=self_harm_score,
            crisis_intent_score=crisis_intent_score,
            distress_score=distress_score,
            violence_score=violence_score,
            lexical_signals=lexical_signals,
        )
        fallback = self._build_fallback_response(risk_level)

        assessment = SafetyAssessmentResponse(
            text=text,
            risk_level=risk_level,
            risk_score=round(risk_score, 4),
            self_harm_score=round(self_harm_score, 4),
            crisis_intent_score=round(crisis_intent_score, 4),
            distress_score=round(distress_score, 4),
            violence_score=round(violence_score, 4),
            policy_action=policy_action,
            should_block_standard_response=should_block_standard_response,
            needs_immediate_escalation=needs_immediate_escalation,
            reasons=reasons,
            lexical_signals=lexical_signals,
            zero_shot_scores=[
                SafetyModelScoreResponse(label=item.label, score=round(item.score, 4))
                for item in zero_shot_scores
            ],
            safe_fallback_response=fallback,
            emergency_resources=get_india_emergency_resources() if include_resources and risk_level in {"high", "critical"} else [],
            model_metadata=self.classifier.metadata(),
            cached=False,
        )
        logger.info(
            "safety_assessment_completed",
            extra={
                "risk_level": risk_level,
                "risk_score": round(risk_score, 4),
                "self_harm_score": round(self_harm_score, 4),
                "crisis_intent_score": round(crisis_intent_score, 4),
            },
        )
        return assessment

    def _lexical_assessment(self, text: str) -> list[SafetyLexicalSignalResponse]:
        lowered = text.lower()
        results: list[SafetyLexicalSignalResponse] = []
        for category, phrases in _RULES.as_mapping().items():
            if category == "unsafe_response_patterns":
                continue
            matched = [phrase for phrase in phrases if phrase in lowered]
            if not matched:
                continue
            score = self._clamp(len(matched) / max(len(phrases) * 0.3, 1.0))
            if category == "explicit_self_harm" and any(
                phrase in lowered for phrase in ("kill myself", "end my life", "take my own life")
            ):
                score = max(score, 0.9)
            results.append(
                SafetyLexicalSignalResponse(
                    category=category,
                    matched_phrases=matched,
                    score=round(score, 4),
                )
            )
        return results

    def _moderate_response_sync(
        self,
        *,
        drafted_response: str,
        assessment: SafetyAssessmentResponse,
    ) -> tuple[str, list[str], str]:
        lowered = drafted_response.lower()
        blocked_flags = [phrase for phrase in _RULES.unsafe_response_patterns if phrase in lowered]

        if assessment.should_block_standard_response:
            return "replace_with_fallback", blocked_flags, assessment.safe_fallback_response

        if blocked_flags:
            sanitized = self._sanitize_response(drafted_response)
            if sanitized != drafted_response:
                return "sanitize", blocked_flags, sanitized
            return "replace_with_fallback", blocked_flags, assessment.safe_fallback_response

        if assessment.risk_level == "moderate":
            moderate_footer = (
                "\n\nIf this starts feeling harder to manage or you feel unsafe, please reach out to a trusted person "
                "or a mental health professional right away."
            )
            return "sanitize", [], f"{drafted_response.strip()}{moderate_footer}"

        return "allow", [], drafted_response

    def _sanitize_response(self, response: str) -> str:
        sanitized = response
        replacements = {
            "you only need me": "it may help to involve supportive people around you",
            "don't tell anyone": "it can help to tell a trusted person or professional",
            "dont tell anyone": "it can help to tell a trusted person or professional",
            "i am your therapist": "I am an AI support tool and not a therapist",
            "just get over it": "what you are feeling matters, and support can help",
        }
        for old, new in replacements.items():
            sanitized = re.sub(re.escape(old), new, sanitized, flags=re.IGNORECASE)
        return sanitized

    def _reasons_from_scores(
        self,
        *,
        self_harm_score: float,
        crisis_intent_score: float,
        distress_score: float,
        violence_score: float,
        lexical_signals: list[SafetyLexicalSignalResponse],
    ) -> list[str]:
        reasons: list[str] = []
        categories = {signal.category for signal in lexical_signals}
        if self_harm_score >= 0.5:
            reasons.append("The text contains elevated self-harm or suicide risk indicators.")
        if crisis_intent_score >= 0.5:
            reasons.append("The text suggests possible immediacy, planning, or inability to stay safe.")
        if distress_score >= 0.45:
            reasons.append("The text reflects severe distress, panic, or hopelessness.")
        if violence_score >= 0.45:
            reasons.append("The text contains possible harm-to-others signals.")
        if "means_or_method" in categories:
            reasons.append("Potential means or method references were detected.")
        return reasons or ["The text does not show strong crisis indicators, but it should still receive supportive handling."]

    def _build_fallback_response(self, risk_level: str) -> str:
        if risk_level == "critical":
            return (
                "I’m really concerned that you may be in immediate danger. Please call emergency services in India right now at 112, "
                "or go to the nearest emergency department. You can also call Tele-MANAS at 14416 or 1-800-891-4416 for immediate mental health support. "
                "If possible, contact a trusted person nearby and tell them you need urgent help now."
            )
        if risk_level == "high":
            return (
                "I’m really sorry you’re carrying this right now. I can stay supportive here, but this sounds serious enough that I strongly want you to reach out to a trusted person immediately. "
                "In India, you can call Tele-MANAS at 14416 or 1-800-891-4416. If you feel you might act on these thoughts or are not safe, call 112 right away."
            )
        if risk_level == "moderate":
            return (
                "I’m sorry this feels so intense right now. Let’s keep the response supportive and grounded. If these feelings get worse, or if you start feeling unsafe, "
                "please contact a trusted person or a mental health professional as soon as you can."
            )
        return (
            "I’m here to support you with empathy and care. I won’t provide harmful or unsafe guidance, but I can help you slow things down and think through supportive next steps."
        )

    def _cache_key(self, text: str, include_resources: bool) -> str:
        raw_key = f"{self._normalize_text(text)}|{include_resources}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def _normalize_text(self, text: str) -> str:
        return _MULTISPACE_PATTERN.sub(" ", text.strip())[: self.settings.safety_text_hard_limit]

    def _clamp(self, value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, value))
