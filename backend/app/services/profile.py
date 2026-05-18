from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.db.models.emergency_contact import EmergencyContact
from app.repositories.profile import ProfileRepository
from app.schemas.profile import (
    EmergencyContactInput,
    QuestionnaireAnswerInput,
    UserWellnessProfileEnvelopeResponse,
    UserWellnessProfileResponse,
    UserWellnessProfileStatusResponse,
    UserWellnessProfileUpsertRequest,
)
from app.services.safety import get_india_emergency_resources


class ProfileService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.profiles = ProfileRepository(session)

    async def get_status(self, *, user_id: str) -> UserWellnessProfileStatusResponse:
        profile = await self.profiles.get_by_user_id(user_id)
        if profile is None or not self._is_v2_completed(profile):
            return UserWellnessProfileStatusResponse(completed=False, trusted_contacts_count=0)

        inferred_risk_level = self._extract_inferred_risk_level(profile.current_state_of_mind)
        return UserWellnessProfileStatusResponse(
            completed=True,
            trusted_contacts_count=len(profile.emergency_contacts),
            inferred_risk_level=inferred_risk_level,
            has_recent_suicidal_thoughts=profile.has_recent_suicidal_thoughts,
            recommended_resources=(
                get_india_emergency_resources()
                if profile.has_recent_suicidal_thoughts and profile.would_like_crisis_resources
                else []
            ),
        )

    async def get_profile(self, *, user_id: str) -> UserWellnessProfileEnvelopeResponse:
        profile = await self.profiles.get_by_user_id(user_id)
        if profile is None or not self._is_v2_completed(profile):
            return UserWellnessProfileEnvelopeResponse(completed=False, profile=None)

        return UserWellnessProfileEnvelopeResponse(
            completed=True,
            profile=self._build_profile_response(profile),
            recommended_resources=(
                get_india_emergency_resources()
                if profile.has_recent_suicidal_thoughts and profile.would_like_crisis_resources
                else []
            ),
        )

    async def upsert_profile(
        self,
        *,
        user_id: str,
        payload: UserWellnessProfileUpsertRequest,
    ) -> UserWellnessProfileEnvelopeResponse:
        profile = await self.profiles.get_by_user_id(user_id)
        if profile is None:
            await self.profiles.create(user_id=user_id)
            profile = await self.profiles.get_by_user_id(user_id)
            if profile is None:
                raise AppException(detail="Profile could not be initialized.", code="profile_not_found")

        analysis = self._analyze_questionnaire(payload.questionnaire_answers)

        profile.current_state_of_mind = analysis["summary"]
        profile.primary_stressors = analysis["stressors"]
        profile.support_goals = payload.support_goals or payload.personal_notes
        profile.has_recent_suicidal_thoughts = bool(analysis["needs_crisis_attention"])
        profile.would_like_crisis_resources = bool(analysis["needs_crisis_attention"])
        profile.allow_contact_reminders_in_high_risk = payload.allow_contact_reminders_in_high_risk
        profile.onboarding_completed_at = datetime.now(UTC)

        contacts = [self._build_contact(contact) for contact in payload.emergency_contacts]
        await self.profiles.replace_emergency_contacts(profile=profile, contacts=contacts)

        await self.session.commit()
        refreshed = await self.profiles.get_by_user_id(user_id)
        if refreshed is None:
            raise AppException(detail="Profile could not be loaded after saving.", code="profile_not_found")

        return UserWellnessProfileEnvelopeResponse(
            completed=True,
            profile=self._build_profile_response(refreshed),
            recommended_resources=(
                get_india_emergency_resources()
                if refreshed.has_recent_suicidal_thoughts and refreshed.would_like_crisis_resources
                else []
            ),
        )

    def _build_contact(self, contact: EmergencyContactInput) -> EmergencyContact:
        return EmergencyContact(
            name=contact.name,
            relationship_to_user=contact.relationship_to_user,
            phone_number=contact.phone_number,
            email=str(contact.email) if contact.email else None,
            notes=contact.notes,
        )

    def _build_profile_response(self, profile) -> UserWellnessProfileResponse:
        return UserWellnessProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            current_state_of_mind=profile.current_state_of_mind,
            primary_stressors=profile.primary_stressors,
            support_goals=profile.support_goals,
            inferred_risk_level=self._extract_inferred_risk_level(profile.current_state_of_mind),
            has_recent_suicidal_thoughts=profile.has_recent_suicidal_thoughts,
            would_like_crisis_resources=profile.would_like_crisis_resources,
            allow_contact_reminders_in_high_risk=profile.allow_contact_reminders_in_high_risk,
            emergency_contacts=profile.emergency_contacts,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            onboarding_completed_at=profile.onboarding_completed_at,
        )

    def _is_v2_completed(self, profile) -> bool:
        return bool(profile.onboarding_completed_at and profile.current_state_of_mind.startswith("Intake v2 |"))

    def _extract_inferred_risk_level(self, summary: str) -> str:
        if "risk=high" in summary:
            return "high"
        if "risk=moderate" in summary:
            return "moderate"
        if "risk=low" in summary:
            return "low"
        return "not_available"

    def _analyze_questionnaire(self, answers: list[QuestionnaireAnswerInput]) -> dict[str, str | bool]:
        score_map = {answer.question_id: answer.score for answer in answers}
        total_score = sum(answer.score for answer in answers)
        distress_cluster = (
            score_map.get("hope", 0)
            + score_map.get("self_worth", 0)
            + score_map.get("grounded_safety", 0)
            + score_map.get("withdrawal", 0)
        )
        stress_cluster = (
            score_map.get("overwhelm", 0)
            + score_map.get("sleep", 0)
            + score_map.get("pressure", 0)
            + score_map.get("panic", 0)
        )
        functioning_cluster = score_map.get("motivation", 0) + score_map.get("support", 0)

        dominant_flags: list[str] = []
        if score_map.get("overwhelm", 0) >= 3 or score_map.get("pressure", 0) >= 3:
            dominant_flags.append("high pressure and overwhelm")
        if score_map.get("sleep", 0) >= 3 or score_map.get("panic", 0) >= 3:
            dominant_flags.append("activated anxiety and sleep disruption")
        if score_map.get("withdrawal", 0) >= 3 or score_map.get("support", 0) >= 3:
            dominant_flags.append("social withdrawal and low felt support")
        if score_map.get("hope", 0) >= 3 or score_map.get("self_worth", 0) >= 3:
            dominant_flags.append("hopelessness and self-worth strain")
        if score_map.get("motivation", 0) >= 3:
            dominant_flags.append("reduced day-to-day motivation")

        needs_crisis_attention = distress_cluster >= 12 or (
            score_map.get("grounded_safety", 0) >= 3 and score_map.get("hope", 0) >= 3
        )
        if needs_crisis_attention:
            inferred_risk = "high"
        elif total_score >= 20 or distress_cluster >= 9:
            inferred_risk = "moderate"
        else:
            inferred_risk = "low"

        summary = (
            f"Intake v2 | risk={inferred_risk} | "
            f"Questionnaire suggests {', '.join(dominant_flags[:3]) or 'mixed but manageable distress signals'}."
        )
        stressor_summary = (
            f"Questionnaire totals: overall={total_score}/40, stress_cluster={stress_cluster}/16, "
            f"distress_cluster={distress_cluster}/16, functioning_cluster={functioning_cluster}/8."
        )
        return {
            "summary": summary,
            "stressors": stressor_summary,
            "needs_crisis_attention": needs_crisis_attention,
        }
