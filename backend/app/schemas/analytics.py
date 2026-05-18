from pydantic import BaseModel


class AnalyticsHeroResponse(BaseModel):
    dominant_emotion: str
    safety_status: str
    weekly_summary: str


class AnalyticsStatResponse(BaseModel):
    title: str
    value: str
    trend: str
    detail: str
    accent: str


class MoodTrendPointResponse(BaseModel):
    day: str
    calm: int
    stress: int
    loneliness: int


class HeatmapCellResponse(BaseModel):
    value: str


class EmotionDistributionPointResponse(BaseModel):
    emotion: str
    share: int
    avg_intensity: int
    color: str


class RiskTrendPointResponse(BaseModel):
    day: str
    avg_risk: int
    elevated: int
    high_alerts: int


class SessionActivityPointResponse(BaseModel):
    day: str
    messages: int
    avg_words: int
    reflection_depth: int


class OperationalInsightResponse(BaseModel):
    title: str
    body: str
    tone: str


class DashboardAnalyticsResponse(BaseModel):
    hero: AnalyticsHeroResponse
    stats: list[AnalyticsStatResponse]
    mood_trend: list[MoodTrendPointResponse]
    heatmap: list[list[HeatmapCellResponse]]
    emotion_distribution: list[EmotionDistributionPointResponse]
    risk_trend: list[RiskTrendPointResponse]
    session_activity: list[SessionActivityPointResponse]
    insights: list[OperationalInsightResponse]


class InsightSummaryResponse(BaseModel):
    title: str
    body: str


class InsightsAnalyticsResponse(BaseModel):
    trend: list[MoodTrendPointResponse]
    heatmap: list[list[HeatmapCellResponse]]
    emotion_distribution: list[EmotionDistributionPointResponse]
    risk_trend: list[RiskTrendPointResponse]
    session_activity: list[SessionActivityPointResponse]
    summaries: list[InsightSummaryResponse]
