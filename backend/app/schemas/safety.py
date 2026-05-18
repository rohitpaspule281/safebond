from typing import Literal

from pydantic import BaseModel, Field


class SafetyEvaluateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    include_resources: bool = True


class SafetyModelScoreResponse(BaseModel):
    label: str
    score: float


class SafetyLexicalSignalResponse(BaseModel):
    category: str
    matched_phrases: list[str]
    score: float


class SafetyEmergencyResourceResponse(BaseModel):
    name: str
    contact: str
    kind: Literal["mental_health", "emergency", "trusted_support"]
    availability: str
    region: str
    source_name: str
    source_url: str


class SafetyAssessmentResponse(BaseModel):
    text: str
    risk_level: Literal["low", "moderate", "high", "critical"]
    risk_score: float
    self_harm_score: float
    crisis_intent_score: float
    distress_score: float
    violence_score: float
    policy_action: str
    should_block_standard_response: bool
    needs_immediate_escalation: bool
    reasons: list[str]
    lexical_signals: list[SafetyLexicalSignalResponse]
    zero_shot_scores: list[SafetyModelScoreResponse]
    safe_fallback_response: str
    emergency_resources: list[SafetyEmergencyResourceResponse] = []
    model_metadata: dict[str, str | bool]
    cached: bool = False


class ResponseModerationRequest(BaseModel):
    user_text: str = Field(min_length=1, max_length=5000)
    drafted_response: str = Field(min_length=1, max_length=8000)
    include_resources: bool = True


class ResponseModerationResponse(BaseModel):
    original_response: str
    moderated_response: str
    action_taken: Literal["allow", "sanitize", "replace_with_fallback"]
    blocked_policy_flags: list[str]
    safety_assessment: SafetyAssessmentResponse


class SafetyResourceCatalogResponse(BaseModel):
    verified_on: str
    resources: list[SafetyEmergencyResourceResponse]
