from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(tags=["health"])


class ServiceInfo(BaseModel):
    service: str
    version: str
    environment: str
    docs: str


class HealthStatus(BaseModel):
    status: Literal["ok"]


@router.get("/", response_model=ServiceInfo, summary="Información del servicio")
def root() -> ServiceInfo:
    """Nombre, versión desplegada (commit) y entorno."""
    return ServiceInfo(
        service="soporteia-api",
        version=settings.app_version,
        environment=settings.environment,
        docs="/docs",
    )


@router.get("/health", response_model=HealthStatus, summary="Health check")
def health() -> HealthStatus:
    """Responde `ok` si el servicio está arriba."""
    return HealthStatus(status="ok")
