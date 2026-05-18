from __future__ import annotations

from app.schemas.safety import ResponseModerationRequest, ResponseModerationResponse
from app.services.safety import SafetyRiskService


class SafetyModerationMiddleware:
    """
    Pipeline middleware for future response-generation agents.

    Intended placement:
    user input -> safety assessment -> generation strategy -> drafted response -> moderation middleware -> final output
    """

    def __init__(self) -> None:
        self.safety_service = SafetyRiskService()

    async def guard_response(
        self,
        *,
        user_text: str,
        drafted_response: str,
        include_resources: bool = True,
    ) -> ResponseModerationResponse:
        return await self.safety_service.moderate_response(
            ResponseModerationRequest(
                user_text=user_text,
                drafted_response=drafted_response,
                include_resources=include_resources,
            )
        )
