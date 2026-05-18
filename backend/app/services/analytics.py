from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.schemas.analytics import (
    AnalyticsHeroResponse,
    EmotionDistributionPointResponse,
    AnalyticsStatResponse,
    DashboardAnalyticsResponse,
    HeatmapCellResponse,
    InsightSummaryResponse,
    InsightsAnalyticsResponse,
    MoodTrendPointResponse,
    OperationalInsightResponse,
    RiskTrendPointResponse,
    SessionActivityPointResponse,
)
from app.schemas.emotion import EmotionAnalysisRequest
from app.schemas.safety import SafetyEvaluateRequest
from app.services.emotion import EmotionAnalysisService
from app.services.safety import SafetyRiskService


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.messages = MessageRepository(session)
        self.conversations = ConversationRepository(session)
        self.emotion_service = EmotionAnalysisService()
        self.safety_service = SafetyRiskService()

    async def dashboard(self, *, user_id: str) -> DashboardAnalyticsResponse:
        user_messages = await self.messages.list_recent_user_messages(user_id=user_id, limit=40)
        analytics = await self._compute_message_analytics(user_messages)
        conversation_count = len(await self.conversations.list_for_user(user_id))

        hero = AnalyticsHeroResponse(
            dominant_emotion=analytics["dominant_emotion"].title(),
            safety_status=analytics["safety_status"].title(),
            weekly_summary=analytics["weekly_summary"],
        )

        stats = [
            AnalyticsStatResponse(
                title="Calm Recovery Index",
                value=f"{analytics['calm_recovery_index']}%",
                trend="+continuity",
                detail="Estimated from recent emotional intensity and calmer-day recovery.",
                accent="from-sage-500/25 to-sage-200/50",
            ),
            AnalyticsStatResponse(
                title="Conversations Indexed",
                value=str(conversation_count),
                trend="Memory online",
                detail="Conversations available for semantic recall and context injection.",
                accent="from-coral-500/20 to-sand-200/50",
            ),
            AnalyticsStatResponse(
                title="Avg Emotional Intensity",
                value=f"{analytics['average_intensity']}%",
                trend=analytics["dominant_emotion"].title(),
                detail="A normalized weekly intensity estimate derived from transformer-based emotion analysis.",
                accent="from-sky-400/20 to-white/70",
            ),
            AnalyticsStatResponse(
                title="Risk Escalations",
                value=str(analytics["elevated_risk_count"]),
                trend=analytics["safety_status"].title(),
                detail="Messages that triggered moderate-or-higher safety routing.",
                accent="from-rose-300/20 to-orange-100/70",
            ),
        ]

        insights = [
            OperationalInsightResponse(
                title="Late-session emotional load",
                body=(
                    f"Recent reflections cluster most strongly around {analytics['dominant_emotion']}, "
                    f"with an average weekly intensity near {analytics['average_intensity']}%."
                ),
                tone="watch",
            ),
            OperationalInsightResponse(
                title="Memory continuity improving support quality",
                body=(
                    f"{conversation_count} indexed conversations are available for semantic recall, "
                    "helping the response layer preserve continuity across sessions."
                ),
                tone="positive",
            ),
            OperationalInsightResponse(
                title="Safety layer remains active",
                body=(
                    f"The recent safety posture is {analytics['safety_status']}, "
                    f"with {analytics['elevated_risk_count']} moderate-or-higher risk detections in the current window."
                ),
                tone="stable",
            ),
            OperationalInsightResponse(
                title="Burnout signatures remain worth tracking",
                body=(
                    f"Reflection depth is averaging {analytics['average_reflection_depth']}%, "
                    "which suggests the user is giving enough detail for meaningful contextual support."
                ),
                tone="watch",
            ),
        ]

        return DashboardAnalyticsResponse(
            hero=hero,
            stats=stats,
            mood_trend=analytics["mood_trend"],
            heatmap=analytics["heatmap"],
            emotion_distribution=analytics["emotion_distribution"],
            risk_trend=analytics["risk_trend"],
            session_activity=analytics["session_activity"],
            insights=insights,
        )

    async def insights(self, *, user_id: str) -> InsightsAnalyticsResponse:
        user_messages = await self.messages.list_recent_user_messages(user_id=user_id, limit=40)
        analytics = await self._compute_message_analytics(user_messages)
        summaries = [
            InsightSummaryResponse(
                title="Dominant emotional signal",
                body=(
                    f"The strongest recent recurring pattern is {analytics['dominant_emotion']}, "
                    f"occupying about {analytics['dominant_share']}% of the analyzed reflection window."
                ),
            ),
            InsightSummaryResponse(
                title="Safety posture",
                body=(
                    f"Recent message safety status is currently assessed as {analytics['safety_status']}, "
                    f"with an average risk signal near {analytics['average_risk']}%."
                ),
            ),
            InsightSummaryResponse(
                title="Longitudinal interpretation",
                body=(
                    "The analytics layer blends emotion intensity, retrieval-ready reflection depth, "
                    "risk scoring, and temporal grouping so the dashboard communicates signals instead of raw message counts."
                ),
            ),
        ]
        return InsightsAnalyticsResponse(
            trend=analytics["mood_trend"],
            heatmap=analytics["heatmap"],
            emotion_distribution=analytics["emotion_distribution"],
            risk_trend=analytics["risk_trend"],
            session_activity=analytics["session_activity"],
            summaries=summaries,
        )

    async def _compute_message_analytics(self, messages) -> dict:
        emotion_palette = {
            "sadness": "#4F7C74",
            "anxiety": "#E86C52",
            "stress": "#B07A46",
            "loneliness": "#5A8FD8",
            "burnout": "#C15D84",
            "anger": "#A253D0",
        }
        now = datetime.now(UTC)
        trend_days = [now.date() - timedelta(days=offset) for offset in range(6, -1, -1)]
        grouped: dict[str, list[dict[str, float | str]]] = defaultdict(list)
        elevated_risk_count = 0
        dominant_counter: dict[str, int] = defaultdict(int)
        intensity_by_emotion: dict[str, list[float]] = defaultdict(list)
        average_confidence = 0.0
        average_risk = 0.0
        average_reflection_depth = 0.0

        for message in messages:
            emotion = await self.emotion_service.analyze(
                EmotionAnalysisRequest(
                    text=message.content,
                    include_explanation=False,
                    top_k=3,
                )
            )
            safety = await self.safety_service.evaluate(
                SafetyEvaluateRequest(text=message.content, include_resources=False)
            )
            if safety.risk_level in {"moderate", "high", "critical"}:
                elevated_risk_count += 1

            dominant_counter[emotion.primary_emotion] += 1
            intensity_by_emotion[emotion.primary_emotion].append(emotion.emotional_intensity)
            day_key = (message.created_at or now).date().isoformat()
            word_count = len(message.content.split())
            grouped[day_key].append(
                {
                    "emotion": emotion.primary_emotion,
                    "intensity": emotion.emotional_intensity,
                    "safety": safety.risk_level,
                    "risk_score": safety.risk_score,
                    "confidence": emotion.confidence,
                    "word_count": float(word_count),
                }
            )
            average_confidence += emotion.confidence
            average_risk += safety.risk_score
            average_reflection_depth += min(1.0, (word_count / 45))

        dominant_emotion = max(dominant_counter, key=dominant_counter.get) if dominant_counter else "stress"
        mood_trend: list[MoodTrendPointResponse] = []
        heatmap_levels: list[list[HeatmapCellResponse]] = []
        risk_trend: list[RiskTrendPointResponse] = []
        session_activity: list[SessionActivityPointResponse] = []
        intensity_values: list[float] = []
        safety_status = "stable"

        for day in trend_days:
            day_entries = grouped.get(day.isoformat(), [])
            if day_entries:
                avg_intensity = sum(float(item["intensity"]) for item in day_entries) / len(day_entries)
                avg_risk_for_day = sum(float(item["risk_score"]) for item in day_entries) / len(day_entries)
                avg_words = round(
                    sum(float(item["word_count"]) for item in day_entries) / len(day_entries)
                )
                stress = round(
                    sum(1 for item in day_entries if item["emotion"] in {"stress", "anxiety", "burnout"})
                    / len(day_entries)
                    * 100
                )
                loneliness = round(
                    sum(1 for item in day_entries if item["emotion"] == "loneliness")
                    / len(day_entries)
                    * 100
                )
                calm = max(20, 100 - round(avg_intensity * 65) - max(stress // 4, 0))
                intensity_values.append(avg_intensity)
                if any(item["safety"] in {"high", "critical"} for item in day_entries):
                    safety_status = "elevated"
            else:
                avg_risk_for_day = 0.18
                avg_words = 0
                stress = 24
                loneliness = 12
                calm = 72
                intensity_values.append(0.3)

            mood_trend.append(
                MoodTrendPointResponse(
                    day=day.strftime("%a"),
                    calm=calm,
                    stress=stress,
                    loneliness=loneliness,
                )
            )
            risk_trend.append(
                RiskTrendPointResponse(
                    day=day.strftime("%a"),
                    avg_risk=round(avg_risk_for_day * 100),
                    elevated=sum(1 for item in day_entries if item["safety"] in {"moderate", "high", "critical"}),
                    high_alerts=sum(1 for item in day_entries if item["safety"] in {"high", "critical"}),
                )
            )
            session_activity.append(
                SessionActivityPointResponse(
                    day=day.strftime("%a"),
                    messages=len(day_entries),
                    avg_words=avg_words,
                    reflection_depth=min(
                        100,
                        round(avg_words * 2.1 + (avg_intensity if day_entries else 0.28) * 35),
                    ),
                )
            )

        padded = intensity_values[:]
        while len(padded) < 28:
            padded.extend(intensity_values or [0.3])
        padded = padded[:28]
        for row_index in range(4):
            row: list[HeatmapCellResponse] = []
            for column_index in range(7):
                value = padded[row_index * 7 + column_index]
                if value >= 0.72:
                    label = "High"
                elif value >= 0.48:
                    label = "Moderate"
                else:
                    label = "Low"
                row.append(HeatmapCellResponse(value=label))
            heatmap_levels.append(row)

        avg_intensity = sum(intensity_values) / len(intensity_values) if intensity_values else 0.3
        message_count = max(len(messages), 1)
        average_confidence = round((average_confidence / message_count) * 100)
        average_risk = round((average_risk / message_count) * 100)
        average_reflection_depth = round((average_reflection_depth / message_count) * 100)
        calm_recovery_index = max(35, min(92, round(100 - avg_intensity * 38 - elevated_risk_count * 2)))
        emotion_distribution = [
            EmotionDistributionPointResponse(
                emotion=emotion.title(),
                share=round((count / message_count) * 100),
                avg_intensity=round(
                    (sum(intensity_by_emotion.get(emotion, [0.0])) / max(len(intensity_by_emotion.get(emotion, [0.0])), 1))
                    * 100
                ),
                color=emotion_palette.get(emotion, "#57796D"),
            )
            for emotion, count in sorted(dominant_counter.items(), key=lambda item: item[1], reverse=True)
        ]
        dominant_share = emotion_distribution[0].share if emotion_distribution else 0
        weekly_summary = (
            f"Recent sessions are leaning toward {dominant_emotion}, "
            f"with an estimated calm recovery index of {calm_recovery_index}% and average model confidence near {average_confidence}%."
        )
        return {
            "dominant_emotion": dominant_emotion,
            "dominant_share": dominant_share,
            "safety_status": safety_status,
            "weekly_summary": weekly_summary,
            "calm_recovery_index": calm_recovery_index,
            "elevated_risk_count": elevated_risk_count,
            "average_intensity": round(avg_intensity * 100),
            "average_confidence": average_confidence,
            "average_risk": average_risk,
            "average_reflection_depth": average_reflection_depth,
            "mood_trend": mood_trend,
            "heatmap": heatmap_levels,
            "emotion_distribution": emotion_distribution,
            "risk_trend": risk_trend,
            "session_activity": session_activity,
        }
