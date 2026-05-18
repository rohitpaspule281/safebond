from app.core.config import get_settings
from app.core.runtime import get_runtime_component_statuses
from app.integrations.chroma import check_chroma_connection
from app.schemas.health import HealthResponse, LivenessResponse, RuntimeComponentStatus, ServiceStatus
from app.db.session import check_database_connection


class HealthService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def liveness(self) -> LivenessResponse:
        return LivenessResponse(status="ok", app_name=self.settings.app_name)

    async def readiness(self) -> HealthResponse:
        services: list[ServiceStatus] = []

        try:
            await check_database_connection()
            services.append(
                ServiceStatus(name="postgresql", status="up", detail="Database connection available.")
            )
        except Exception:
            services.append(
                ServiceStatus(
                    name="postgresql",
                    status="down",
                    detail="Database connection unavailable.",
                )
            )

        try:
            check_chroma_connection()
            services.append(
                ServiceStatus(name="chromadb", status="up", detail="Vector store reachable.")
            )
        except Exception:
            services.append(
                ServiceStatus(name="chromadb", status="down", detail="Vector store unavailable.")
            )

        overall = "ok" if all(service.status == "up" for service in services) else "degraded"
        return HealthResponse(
            status=overall,
            app_name=self.settings.app_name,
            environment=self.settings.app_env,
            version=self.settings.app_version,
            services=services,
            runtime=[
                RuntimeComponentStatus(
                    name=item.name,
                    status=item.status,
                    detail=item.detail,
                    warmed_at=item.warmed_at,
                )
                for item in get_runtime_component_statuses()
            ],
        )
