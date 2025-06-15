# backend/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import machines, metrics, configuration, alerts, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(configuration.router, prefix="/configuration", tags=["configuration"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])