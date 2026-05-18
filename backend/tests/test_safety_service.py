import pytest

from app.schemas.safety import ResponseModerationRequest, SafetyEvaluateRequest
from app.services import safety as safety_module


class FakeZeroShotClassifier:
    def classify(self, *, text: str, candidate_labels: list[str], multi_label: bool = True):
        base = {
            "self-harm or suicide risk": 0.12,
            "acute crisis or imminent danger": 0.08,
            "severe emotional distress or panic": 0.22,
            "violence or harm to others risk": 0.03,
            "request for general emotional support": 0.70,
        }
        lowered = text.lower()
        if "kill myself" in lowered or "end my life" in lowered:
            base["self-harm or suicide risk"] = 0.88
            base["acute crisis or imminent danger"] = 0.79
            base["severe emotional distress or panic"] = 0.74
            base["request for general emotional support"] = 0.10
        return [
            type("Label", (), {"label": label, "score": score})()
            for label, score in base.items()
            if label in candidate_labels
        ]

    def metadata(self):
        return {"model_name": "fake-safety-model", "device": "cpu", "loaded": True}


@pytest.mark.asyncio
async def test_safety_service_detects_critical_self_harm_risk(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(safety_module, "get_safety_zero_shot_classifier", lambda: FakeZeroShotClassifier())
    service = safety_module.SafetyRiskService()

    response = await service.evaluate(
        SafetyEvaluateRequest(text="I want to kill myself tonight and I have pills ready.")
    )

    assert response.risk_level in {"high", "critical"}
    assert response.self_harm_score >= 0.62
    assert response.should_block_standard_response is True
    assert len(response.reasons) >= 1


@pytest.mark.asyncio
async def test_response_moderation_replaces_unsafe_draft(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(safety_module, "get_safety_zero_shot_classifier", lambda: FakeZeroShotClassifier())
    service = safety_module.SafetyRiskService()

    response = await service.moderate_response(
        ResponseModerationRequest(
            user_text="I want to end my life tonight.",
            drafted_response="Here is how to hurt yourself and don't tell anyone.",
        )
    )

    assert response.action_taken == "replace_with_fallback"
    assert response.safety_assessment.should_block_standard_response is True
    assert "Tele-MANAS" in response.moderated_response or "112" in response.moderated_response
