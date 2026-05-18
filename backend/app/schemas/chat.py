from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.conversation import ConversationResponse, MessageResponse
from app.schemas.emotion import EmotionAnalysisResponse
from app.schemas.memory import ContextRetrieveResponse
from app.schemas.safety import ResponseModerationResponse, SafetyAssessmentResponse


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    conversation_id: str | None = None
    title: str | None = Field(default=None, min_length=2, max_length=160)


class ResponseStrategyResponse(BaseModel):
    key: Literal[
        "validation",
        "grounding",
        "reflection",
        "reframing",
        "action_step",
        "memory_continuity",
        "containment",
    ]
    label: str
    rationale: str


class SupportActionResponse(BaseModel):
    kind: Literal[
        "reflect",
        "ground",
        "journal",
        "reach_out",
        "call_trusted_contact",
        "text_trusted_contact",
        "view_crisis_resources",
    ]
    label: str
    description: str
    priority: Literal["normal", "important", "urgent"]


class TrustedContactOutreachOptionResponse(BaseModel):
    contact_id: str
    name: str
    relationship_to_user: str
    phone_number: str | None
    email: str | None
    why_now: str
    sms_message: str | None
    email_subject: str | None
    email_body: str | None
    call_recommended: bool = False


class ChatResponse(BaseModel):
    conversation: ConversationResponse
    user_message: MessageResponse
    assistant_message: MessageResponse
    emotion: EmotionAnalysisResponse
    safety: SafetyAssessmentResponse
    rag_context: ContextRetrieveResponse
    moderation: ResponseModerationResponse
    response_strategy: ResponseStrategyResponse
    support_actions: list[SupportActionResponse] = []
    trusted_contact_options: list[TrustedContactOutreachOptionResponse] = []
