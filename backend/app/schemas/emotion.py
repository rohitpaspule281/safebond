from pydantic import BaseModel, Field


class EmotionAnalysisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    include_explanation: bool = True
    top_k: int = Field(default=3, ge=2, le=6)


class BatchEmotionAnalysisRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=16)
    include_explanation: bool = True
    top_k: int = Field(default=3, ge=2, le=6)


class LabelScoreResponse(BaseModel):
    label: str
    score: float


class SentimentSummaryResponse(BaseModel):
    label: str
    score: float


class HighlightedSegmentResponse(BaseModel):
    text: str
    matched_emotion: str
    score: float


class ConfidenceBreakdownResponse(BaseModel):
    primary_score: float
    label_margin: float
    sentiment_support: float
    cue_support: float
    agreement_bonus: float


class ExplainabilityResponse(BaseModel):
    reasoning: str
    lexical_cues: list[str]
    highlighted_segments: list[HighlightedSegmentResponse]
    model_emotions: list[LabelScoreResponse]
    model_sentiments: list[LabelScoreResponse]
    confidence_breakdown: ConfidenceBreakdownResponse


class EmotionModelInfoResponse(BaseModel):
    role: str
    model_name: str
    device: str
    max_length: int
    loaded: bool


class EmotionAnalysisResponse(BaseModel):
    text: str
    primary_emotion: str
    secondary_emotion: str | None = None
    emotional_intensity: float
    confidence: float
    top_emotions: list[LabelScoreResponse]
    sentiment: SentimentSummaryResponse
    sentiment_distribution: list[LabelScoreResponse]
    explanation: ExplainabilityResponse | None = None
    model_metadata: list[EmotionModelInfoResponse]
    cached: bool = False


class BatchEmotionAnalysisResponse(BaseModel):
    results: list[EmotionAnalysisResponse]


class EmotionModelCatalogResponse(BaseModel):
    models: list[EmotionModelInfoResponse]
