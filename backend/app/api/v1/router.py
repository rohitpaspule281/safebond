from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.conversation import router as conversation_router
from app.api.v1.endpoints.emotion import router as emotion_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.memory import router as memory_router
from app.api.v1.endpoints.profile import router as profile_router
from app.api.v1.endpoints.safety import router as safety_router

api_router = APIRouter()
api_router.include_router(analytics_router)
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(conversation_router)
api_router.include_router(emotion_router)
api_router.include_router(health_router)
api_router.include_router(memory_router)
api_router.include_router(profile_router)
api_router.include_router(safety_router)
