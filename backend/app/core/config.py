from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Safebond API"
    app_env: Literal["development", "staging", "production", "test"] = "development"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"
    app_version: str = "0.1.0"

    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    database_url: str = "postgresql+asyncpg://safebond:safebond@localhost:5432/safebond"
    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_auto_create_tables: bool = False

    vector_store_provider: str = "chroma"
    chroma_mode: Literal["local", "http"] = "local"
    chroma_persist_directory: str = "./chroma"
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_ssl: bool = False
    chroma_collection_prefix: str = "safebond"

    llm_provider: str = "groq"
    llm_model: str = "llama-3.1-8b-instant"
    groq_api_key: str | None = None
    gemini_api_key: str | None = None

    emotion_model_name: str = "j-hartmann/emotion-english-distilroberta-base"
    sentiment_model_name: str = "cardiffnlp/twitter-roberta-base-sentiment"
    emotion_device_preference: Literal["auto", "cpu", "cuda"] = "auto"
    emotion_max_length: int = 256
    sentiment_max_length: int = 256
    emotion_cache_ttl_seconds: int = 1800
    emotion_cache_max_size: int = 512
    emotion_text_hard_limit: int = 4000
    emotion_max_explanation_segments: int = 3
    hf_local_files_only: bool = False
    torch_num_threads: int | None = None
    memory_embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device_preference: Literal["auto", "cpu", "cuda"] = "auto"
    memory_chunk_size_chars: int = 420
    memory_chunk_overlap_sentences: int = 1
    memory_text_hard_limit: int = 8000
    memory_candidate_multiplier: int = 3
    memory_semantic_weight: float = 0.6
    memory_recency_weight: float = 0.2
    memory_importance_weight: float = 0.15
    memory_same_conversation_boost: float = 0.05
    memory_recency_half_life_hours: int = 168
    memory_index_assistant_messages: bool = True
    safety_zero_shot_model_name: str = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
    safety_device_preference: Literal["auto", "cpu", "cuda"] = "auto"
    safety_text_hard_limit: int = 5000
    safety_cache_ttl_seconds: int = 900
    safety_cache_max_size: int = 512
    safety_moderate_threshold: float = 0.35
    safety_high_threshold: float = 0.58
    safety_critical_threshold: float = 0.78
    safety_self_harm_threshold: float = 0.62
    model_warmup_on_startup: bool = True

    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
