from __future__ import annotations

import hashlib
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.profile import ProfileRepository
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ResponseStrategyResponse,
    SupportActionResponse,
    TrustedContactOutreachOptionResponse,
)
from app.schemas.conversation import ConversationCreateRequest, MessageCreateRequest
from app.schemas.emotion import EmotionAnalysisRequest
from app.schemas.memory import ContextRetrieveRequest
from app.schemas.safety import ResponseModerationRequest, SafetyEvaluateRequest
from app.services.emotion import EmotionAnalysisService
from app.services.memory import ConversationalMemoryService
from app.services.rag import RAGContextService
from app.services.safety import SafetyRiskService


class ChatOrchestrationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.memory_service = ConversationalMemoryService(session)
        self.rag_service = RAGContextService(session)
        self.emotion_service = EmotionAnalysisService()
        self.safety_service = SafetyRiskService()
        self.profile_repository = ProfileRepository(session)

    async def handle_chat(self, *, user_id: str, payload: ChatRequest) -> ChatResponse:
        if payload.conversation_id:
            conversation_detail = await self.memory_service.get_conversation_detail(
                user_id=user_id,
                conversation_id=payload.conversation_id,
            )
            conversation = conversation_detail.conversation
        else:
            conversation = await self.memory_service.create_conversation(
                user_id=user_id,
                payload=ConversationCreateRequest(title=payload.title or "New reflection"),
            )
        profile = await self.profile_repository.get_by_user_id(user_id)

        safety = await self.safety_service.evaluate(
            SafetyEvaluateRequest(text=payload.message, include_resources=True)
        )
        emotion = await self.emotion_service.analyze(
            EmotionAnalysisRequest(text=payload.message, include_explanation=True)
        )

        user_message = await self.memory_service.add_message(
            user_id=user_id,
            conversation_id=conversation.id,
            payload=MessageCreateRequest(
                role="user",
                content=payload.message,
                index_for_memory=True,
            ),
        )

        rag_context = await self.rag_service.build_context(
            user_id=user_id,
            payload=ContextRetrieveRequest(
                query=payload.message,
                conversation_id=conversation.id,
                top_k=5,
            ),
            exclude_message_ids=[user_message.id],
        )

        response_strategy = self._select_response_strategy(
            emotion_label=emotion.primary_emotion,
            emotion_intensity=emotion.emotional_intensity,
            safety_level=safety.risk_level,
            rag_context=rag_context.injected_context,
        )
        drafted_response = self._draft_supportive_response(
            user_text=payload.message,
            emotion_label=emotion.primary_emotion,
            emotion_intensity=emotion.emotional_intensity,
            rag_context=rag_context.injected_context,
            safety_level=safety.risk_level,
            strategy=response_strategy,
            support_goals=(profile.support_goals if profile else None),
        )

        moderation = await self.safety_service.moderate_response(
            ResponseModerationRequest(
                user_text=payload.message,
                drafted_response=drafted_response,
                include_resources=True,
            )
        )

        assistant_message = await self.memory_service.add_message(
            user_id=user_id,
            conversation_id=conversation.id,
            payload=MessageCreateRequest(
                role="assistant",
                content=moderation.moderated_response,
                index_for_memory=True,
            ),
        )

        refreshed_conversation = await self.memory_service.get_conversation_detail(
            user_id=user_id,
            conversation_id=conversation.id,
        )
        trusted_contact_options = self._build_trusted_contact_options(
            profile=profile,
            safety_level=safety.risk_level,
            user_text=payload.message,
        )
        support_actions = self._build_support_actions(
            emotion_label=emotion.primary_emotion,
            safety_level=safety.risk_level,
            strategy=response_strategy,
            has_memory_context=bool(rag_context.retrieved_memories),
            has_trusted_contact=bool(trusted_contact_options),
        )
        return ChatResponse(
            conversation=refreshed_conversation.conversation,
            user_message=user_message,
            assistant_message=assistant_message,
            emotion=emotion,
            safety=safety,
            rag_context=rag_context,
            moderation=moderation,
            response_strategy=response_strategy,
            support_actions=support_actions,
            trusted_contact_options=trusted_contact_options,
        )

    def _select_response_strategy(
        self,
        *,
        emotion_label: str,
        emotion_intensity: float,
        safety_level: str,
        rag_context: str,
    ) -> ResponseStrategyResponse:
        if safety_level in {"high", "critical"}:
            return ResponseStrategyResponse(
                key="containment",
                label="Safety mode",
                rationale="Risk is elevated, so Safebond shifts from reflection into immediate stabilization and human support."
            )
        if emotion_label in {"anxiety", "stress"} and emotion_intensity >= 0.66:
            return ResponseStrategyResponse(
                key="grounding",
                label="Calm mode",
                rationale="The emotional signal looks activated, so the response prioritizes steadiness, pacing, and the next manageable step."
            )
        if emotion_label == "anger":
            return ResponseStrategyResponse(
                key="reframing",
                label="Clarity mode",
                rationale="The response acknowledges emotional heat while slowing interpretation and protecting against impulsive action."
            )
        if rag_context.strip():
            return ResponseStrategyResponse(
                key="memory_continuity",
                label="Pattern mode",
                rationale="Safebond found meaningful overlap with earlier reflections, so the response connects the current moment to a broader pattern."
            )
        if emotion_label in {"sadness", "loneliness", "burnout"}:
            return ResponseStrategyResponse(
                key="validation",
                label="Gentle support mode",
                rationale="The emotional pattern benefits from steady validation before moving into problem-solving."
            )
        if emotion_intensity < 0.45:
            return ResponseStrategyResponse(
                key="action_step",
                label="Action mode",
                rationale="The intensity looks workable, so the response can move more quickly toward one concrete next step."
            )
        return ResponseStrategyResponse(
            key="reflection",
            label="Reflective mode",
            rationale="The system is balancing empathy with gentle reflection to help the user name what feels most immediate."
        )

    def _draft_supportive_response(
        self,
        *,
        user_text: str,
        emotion_label: str,
        emotion_intensity: float,
        rag_context: str,
        safety_level: str,
        strategy: ResponseStrategyResponse,
        support_goals: str | None,
    ) -> str:
        if safety_level in {"high", "critical"}:
            immediate_step = self._build_concrete_step(
                emotion_label=emotion_label,
                strategy_key="containment",
                user_text=user_text,
            )
            return self._format_response(
                "I’m really glad you said this out loud. I’m staying with you and keeping this very practical.",
                immediate_step,
                "If you can, reach a real person right now, especially a trusted contact or crisis support line, rather than trying to carry this alone."
            )

        opener_banks = {
            "validation": [
                "What you’re describing feels heavy, and I want to meet it gently.",
                "There’s a real weight in this, and it makes sense that it is affecting you.",
                "You do not sound dramatic here, you sound worn down by something that matters."
            ],
            "grounding": [
                "Your system sounds activated right now, so I want to respond in a steadier, slower way.",
                "This reads like a lot of pressure landing in your body and mind at once.",
                "It makes sense that your thoughts feel fast when the emotional load is this high."
            ],
            "reflection": [
                "I’m hearing more than one layer in this, and it may help to name the part that feels most immediate.",
                "There’s a lot happening underneath this message, not just one emotion.",
                "This feels like a moment where reflection may help us separate signal from overload."
            ],
            "reframing": [
                "There is a lot of emotional heat here, and that does not make your reaction irrational.",
                "Your frustration makes sense, even if the moment is pulling you toward a harsh conclusion.",
                "Something important is being violated for you here, and that is part of why it feels so sharp."
            ],
            "action_step": [
                "This feels workable enough that we can focus on the next step instead of the whole problem.",
                "There may be room here to reduce the pressure by choosing one small action.",
                "We do not have to solve everything at once to make this moment a little better."
            ],
            "memory_continuity": [
                "I’m noticing continuity with things you’ve shared before, not just a one-off hard moment.",
                "This seems connected to a pattern that has been showing up across your reflections.",
                "There’s a thread here that Safebond has seen before, and that continuity matters."
            ],
        }
        middle_banks = {
            "anxiety": [
                "A good move is to shrink the horizon to the next ten minutes instead of the entire future.",
                "It may help to separate what is urgent from what is simply loud in your head right now.",
                "The goal is not to win the whole day immediately, only to make this moment more survivable."
            ],
            "stress": [
                "Pressure often makes everything feel equally urgent, even when it is not.",
                "Sometimes the nervous system treats unfinished tasks like emergencies, even when they are just unresolved.",
                "This may be a moment to sort signal from noise before taking another step."
            ],
            "sadness": [
                "We can keep this small and honest rather than forcing a positive spin onto it.",
                "It may help to name the part that feels hardest to carry alone instead of summarizing the whole day.",
                "You do not have to turn this into a lesson right away for it to deserve care."
            ],
            "loneliness": [
                "Feeling alone with your thoughts can make them sound more absolute than they really are.",
                "When isolation grows, even brief contact with a trusted person can change the emotional temperature.",
                "It may matter less to explain yourself perfectly and more to not be alone in this moment."
            ],
            "burnout": [
                "This sounds less like a productivity problem and more like sustained depletion.",
                "Recovery may matter more here than optimizing your effort for one more push.",
                "Burnout often disguises itself as personal failure when it is actually accumulated overload."
            ],
            "anger": [
                "Before acting, it may help to slow the story your mind is building about what this moment means.",
                "Anger often points to something important, but it does not always give the clearest next instruction.",
                "You may not need to suppress the anger, only create enough space to choose how to use it."
            ],
        }
        closers = {
            "validation": [
                "If you want, we can stay with the hardest part first instead of trying to tidy it up.",
                "If you want, we can keep this gentle and start with the piece that feels heaviest.",
                "If you want, we can keep going by naming what feels most painful or most tiring."
            ],
            "grounding": [
                "If you want, we can ground this further by choosing one tiny action for the next few minutes.",
                "If you want, we can slow things down together and pick the next manageable step.",
                "If you want, we can stay concrete and focus on what would help your body feel 5 percent safer."
            ],
            "reflection": [
                "If you want, we can unpack which part is fear, which part is pressure, and which part is grief.",
                "If you want, we can keep reflecting until the situation feels more named and less foggy.",
                "If you want, we can pull apart the immediate trigger from the deeper theme underneath it."
            ],
            "reframing": [
                "If you want, we can look for the boundary or need underneath the anger before deciding what action fits.",
                "If you want, we can turn that emotional heat into a clearer next move instead of a fast reaction.",
                "If you want, we can slow this down enough to protect your judgment without dismissing what you feel."
            ],
            "action_step": [
                "If you want, we can turn this into one concrete next action right now.",
                "If you want, we can choose a single step that reduces the load without pretending everything is solved.",
                "If you want, we can make the next step specific enough that it feels doable."
            ],
            "memory_continuity": [
                "If you want, we can use that pattern to figure out what tends to help and what keeps pulling you back here.",
                "If you want, we can explore what this recurring thread is asking for rather than treating it like a random bad moment.",
                "If you want, we can connect this with earlier reflections and look for the smallest leverage point."
            ],
        }

        memory_line = ""
        context_lines = [line for line in rag_context.splitlines() if line.startswith("[Memory ")]
        if context_lines:
            memory_line = (
                " I’m also noticing continuity with earlier moments you shared, especially around "
                f"{context_lines[0].split(':', 1)[-1].strip()[:120]}."
            )

        intensity_line = (
            " The emotional intensity looks elevated right now."
            if emotion_intensity >= 0.7
            else " The intensity looks present but still workable."
        )
        goal_line = ""
        if support_goals:
            goal_line = f" I’m keeping your earlier goal in mind too: {support_goals[:120].strip()}."
        focus_line = self._build_focus_line(user_text=user_text)
        practical_step = self._build_concrete_step(
            emotion_label=emotion_label,
            strategy_key=strategy.key,
            user_text=user_text,
        )
        follow_up = self._build_follow_up_question(
            emotion_label=emotion_label,
            strategy_key=strategy.key,
            user_text=user_text,
        )

        opener = self._pick_variant(
            seed=f"{user_text}:{strategy.key}:opener",
            options=opener_banks.get(strategy.key, opener_banks["reflection"]),
        )
        middle = self._pick_variant(
            seed=f"{user_text}:{emotion_label}:middle",
            options=middle_banks.get(emotion_label, middle_banks["stress"]),
        )
        closer = self._pick_variant(
            seed=f"{user_text}:{strategy.key}:closer",
            options=closers.get(strategy.key, closers["reflection"]),
        )

        first_paragraph = f"{opener}{focus_line}{memory_line}".strip()
        second_paragraph = f"{middle}{goal_line}{intensity_line} {practical_step}".strip()

        return self._format_response(
            first_paragraph,
            second_paragraph,
            f"{closer} {follow_up}".strip(),
        )

    def _format_response(self, *parts: str) -> str:
        cleaned_parts = [part.strip() for part in parts if part and part.strip()]
        return "\n\n".join(cleaned_parts)

    def _build_focus_line(self, *, user_text: str) -> str:
        normalized = " ".join(user_text.strip().split())
        if not normalized:
            return ""

        first_sentence = re.split(r"(?<=[.!?])\s+", normalized, maxsplit=1)[0].strip()
        if len(first_sentence) > 110:
            first_sentence = f"{first_sentence[:107].rstrip()}..."
        return f" I’m hearing: \"{first_sentence}\"."

    def _build_concrete_step(
        self,
        *,
        emotion_label: str,
        strategy_key: str,
        user_text: str,
    ) -> str:
        lowered = user_text.lower()
        if strategy_key == "containment":
            return (
                "For the next few minutes, focus only on safety: move away from anything you could use to hurt yourself, and get closer to another person if you can."
            )
        if "sleep" in lowered or "tired" in lowered or "insomnia" in lowered:
            return (
                "For tonight, step away from the problem for ten minutes and give your body one calmer cue like water, slower breathing, or a quieter space."
            )
        if "project" in lowered or "exam" in lowered or "deadline" in lowered or "assignment" in lowered:
            return (
                "Try writing down the single next task, not the whole project, and give it just ten focused minutes."
            )
        if "alone" in lowered or "lonely" in lowered or "nobody" in lowered:
            return (
                "A helpful next step may be to break the isolation with one honest message to someone safe, even if it is just: \"I’m having a hard moment and could use some company.\""
            )
        if emotion_label in {"anxiety", "stress"}:
            return (
                "Right now, choose one thing your body can do and one thing your mind can ignore for the next ten minutes."
            )
        if emotion_label in {"sadness", "loneliness"}:
            return (
                "A gentle next step could be naming what hurts most in one sentence instead of carrying the whole emotional pile at once."
            )
        if emotion_label == "burnout":
            return (
                "A better next step may be reducing the load for today, even slightly, instead of asking yourself to push harder."
            )
        if emotion_label == "anger":
            return (
                "Before you act, pause long enough to decide what outcome you actually want from this moment."
            )
        return "Let’s keep the next move small enough that it feels doable, not impressive."

    def _build_follow_up_question(
        self,
        *,
        emotion_label: str,
        strategy_key: str,
        user_text: str,
    ) -> str:
        lowered = user_text.lower()
        if strategy_key == "containment":
            return "Can you tell me whether you are alone right now, or whether there is someone nearby you can contact immediately?"
        if "project" in lowered or "deadline" in lowered or "exam" in lowered:
            return "What is the very next task that feels stuck or intimidating right now?"
        if "sleep" in lowered or "tired" in lowered:
            return "What usually makes nights worse for you, and what has helped even a little in the past?"
        if "alone" in lowered or "lonely" in lowered:
            return "Who feels safest or least draining to reach out to, even if you do not feel like explaining everything?"
        if emotion_label in {"anxiety", "stress"}:
            return "What feels most urgent in your head right now, and what is actually the next thing in front of you?"
        if emotion_label in {"sadness", "burnout"}:
            return "What has been the hardest part to carry by yourself today?"
        if emotion_label == "anger":
            return "What boundary, disappointment, or pressure do you think this anger is pointing toward?"
        return "What feels most immediate for you right now: pressure, fear, exhaustion, or feeling alone?"

    def _build_support_actions(
        self,
        *,
        emotion_label: str,
        safety_level: str,
        strategy: ResponseStrategyResponse,
        has_memory_context: bool,
        has_trusted_contact: bool,
    ) -> list[SupportActionResponse]:
        actions: list[SupportActionResponse] = []
        if strategy.key == "grounding":
            actions.append(
                SupportActionResponse(
                    kind="ground",
                    label="Do one grounding step",
                    description="Shrink the horizon to the next ten minutes and focus on one calming action.",
                    priority="important",
                )
            )
        elif strategy.key == "memory_continuity" and has_memory_context:
            actions.append(
                SupportActionResponse(
                    kind="journal",
                    label="Notice the recurring pattern",
                    description="Use this moment to name what keeps repeating and what usually helps.",
                    priority="normal",
                )
            )
        elif strategy.key in {"validation", "reflection"}:
            actions.append(
                SupportActionResponse(
                    kind="reflect",
                    label="Name the heaviest part",
                    description="Try identifying the part of the situation that feels most immediate or most painful.",
                    priority="normal",
                )
            )
        elif strategy.key == "reframing":
            actions.append(
                SupportActionResponse(
                    kind="journal",
                    label="Pause before reacting",
                    description="Write down the need or boundary under the anger before deciding what to do next.",
                    priority="important",
                )
            )
        else:
            actions.append(
                SupportActionResponse(
                    kind="journal",
                    label="Choose one next step",
                    description="Reduce the load by deciding on a single concrete action instead of the whole plan.",
                    priority="normal",
                )
            )

        if emotion_label in {"loneliness", "sadness"} and safety_level in {"low", "moderate"}:
            actions.append(
                SupportActionResponse(
                    kind="reach_out",
                    label="Reach toward someone safe",
                    description="Even a short text to a trusted person can reduce the sense of carrying this alone.",
                    priority="important",
                )
            )

        if safety_level in {"high", "critical"}:
            actions.append(
                SupportActionResponse(
                    kind="view_crisis_resources",
                    label="Use crisis support now",
                    description="Move from reflection to immediate human support and keep the next action concrete.",
                    priority="urgent",
                )
            )
            if has_trusted_contact:
                actions.extend(
                    [
                        SupportActionResponse(
                            kind="text_trusted_contact",
                            label="Text your trusted contact",
                            description="Use the contact you saved during onboarding so you are not managing this alone.",
                            priority="urgent",
                        ),
                        SupportActionResponse(
                            kind="call_trusted_contact",
                            label="Call your trusted contact",
                            description="If texting is not enough, move straight to a real-time voice conversation.",
                            priority="urgent",
                        ),
                    ]
                )

        return actions

    def _build_trusted_contact_options(
        self,
        *,
        profile,
        safety_level: str,
        user_text: str,
    ) -> list[TrustedContactOutreachOptionResponse]:
        if (
            profile is None
            or not profile.allow_contact_reminders_in_high_risk
            or not getattr(profile, "emergency_contacts", None)
            or safety_level not in {"high", "critical"}
        ):
            return []

        why_now = (
            "Safebond is seeing elevated risk signals, so reaching a trusted person is a safer next step than staying alone with this."
        )
        sms_message = (
            "Hi, I am having a really difficult emotional moment right now and could use support. "
            "Can you call or text me as soon as you can? I am reaching out because staying connected feels important."
        )
        email_subject = "I could use support right now"
        email_body = (
            "Hi,\n\n"
            "I am having a difficult emotional moment right now and I would really value your support. "
            "If you are able, please call or message me when you can.\n\n"
            f"I was reflecting on: \"{user_text[:180].strip()}\"\n\n"
            "Reaching out feels important right now.\n"
        )

        options: list[TrustedContactOutreachOptionResponse] = []
        for contact in profile.emergency_contacts:
            options.append(
                TrustedContactOutreachOptionResponse(
                    contact_id=contact.id,
                    name=contact.name,
                    relationship_to_user=contact.relationship_to_user,
                    phone_number=contact.phone_number,
                    email=contact.email,
                    why_now=why_now,
                    sms_message=sms_message if contact.phone_number else None,
                    email_subject=email_subject if contact.email else None,
                    email_body=email_body if contact.email else None,
                    call_recommended=bool(contact.phone_number),
                )
            )
        return options

    def _pick_variant(self, *, seed: str, options: list[str]) -> str:
        if not options:
            return ""
        index = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % len(options)
        return options[index]
