from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.schemas.safety import SafetyEmergencyResourceResponse


class EmergencyContactInput(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    relationship_to_user: str = Field(min_length=2, max_length=80)
    phone_number: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None
    notes: str | None = Field(default=None, max_length=240)

    @field_validator("phone_number", "notes", mode="before")
    @classmethod
    def blank_to_none(cls, value: str | None):
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @model_validator(mode="after")
    def validate_contact_method(self):
        if not self.phone_number and not self.email:
            raise ValueError("Add at least a phone number or email for each trusted contact.")
        return self


class EmergencyContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    relationship_to_user: str
    phone_number: str | None
    email: EmailStr | None
    notes: str | None
    created_at: datetime


class QuestionnaireAnswerInput(BaseModel):
    question_id: str
    prompt: str = Field(min_length=8, max_length=240)
    score: int = Field(ge=0, le=4)


class UserWellnessProfileUpsertRequest(BaseModel):
    questionnaire_answers: list[QuestionnaireAnswerInput] = Field(min_length=10, max_length=12)
    support_goals: str | None = Field(default=None, max_length=600)
    personal_notes: str | None = Field(default=None, max_length=600)
    allow_contact_reminders_in_high_risk: bool = False
    emergency_contacts: list[EmergencyContactInput] = Field(min_length=1, max_length=3)

    @field_validator("support_goals", "personal_notes", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: str | None):
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @model_validator(mode="after")
    def validate_high_risk_preferences(self):
        question_ids = {answer.question_id for answer in self.questionnaire_answers}
        required_ids = {
            "overwhelm",
            "sleep",
            "withdrawal",
            "hope",
            "motivation",
            "pressure",
            "self_worth",
            "grounded_safety",
            "panic",
            "support",
        }
        if not required_ids.issubset(question_ids):
            raise ValueError("All questionnaire questions must be answered before continuing.")
        return self


class UserWellnessProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    current_state_of_mind: str
    primary_stressors: str | None
    support_goals: str | None
    inferred_risk_level: str
    has_recent_suicidal_thoughts: bool
    would_like_crisis_resources: bool
    allow_contact_reminders_in_high_risk: bool
    emergency_contacts: list[EmergencyContactResponse]
    created_at: datetime
    updated_at: datetime
    onboarding_completed_at: datetime | None


class UserWellnessProfileStatusResponse(BaseModel):
    completed: bool
    trusted_contacts_count: int
    inferred_risk_level: str = "not_available"
    has_recent_suicidal_thoughts: bool = False
    recommended_resources: list[SafetyEmergencyResourceResponse] = Field(default_factory=list)


class UserWellnessProfileEnvelopeResponse(BaseModel):
    completed: bool
    profile: UserWellnessProfileResponse | None = None
    recommended_resources: list[SafetyEmergencyResourceResponse] = Field(default_factory=list)
