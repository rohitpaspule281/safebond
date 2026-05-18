from typing import Literal

from pydantic import BaseModel


class ServiceStatus(BaseModel):
    name: str
    status: Literal["up", "down"]
    detail: str


class RuntimeComponentStatus(BaseModel):
    name: str
    status: Literal["pending", "warming", "ready", "error"]
    detail: str
    warmed_at: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    app_name: str
    environment: str
    version: str
    services: list[ServiceStatus]
    runtime: list[RuntimeComponentStatus] = []


class LivenessResponse(BaseModel):
    status: Literal["ok"]
    app_name: str
