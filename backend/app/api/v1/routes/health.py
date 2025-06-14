from fastapi import APIRouter, Request
from typing import Dict, Any
from datetime import datetime
import psutil
import sys

router = APIRouter()

@router.get("/")
async def health_check(request: Request) -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/ready")
async def ready_check(request: Request) -> Dict[str, Any]:
    """Readiness check with detailed system info"""
    try:
        machines_store = request.app.state.machines_store
        metrics_store = request.app.state.metrics_store
        alerts_store = request.app.state.alerts_store
        websocket_manager = request.app.state.websocket_manager
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "machines": {
                    "status": "healthy",
                    "count": len(machines_store)
                },
                "metrics": {
                    "status": "healthy", 
                    "count": sum(len(metrics) for metrics in metrics_store.values())
                },
                "alerts": {
                    "status": "healthy",
                    "total": len(alerts_store),
                    "active": len([a for a in alerts_store if a.get("is_active", True)])
                },
                "websocket": {
                    "status": "healthy",
                    "connections": websocket_manager.get_connection_count()
                }
            },
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "python_version": sys.version
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/metrics")
async def metrics_endpoint(request: Request) -> Dict[str, Any]:
    """Prometheus-style metrics endpoint"""
    try:
        machines_store = request.app.state.machines_store
        metrics_store = request.app.state.metrics_store
        alerts_store = request.app.state.alerts_store
        websocket_manager = request.app.state.websocket_manager
        
        total_metrics = sum(len(metrics) for metrics in metrics_store.values())
        active_alerts = len([a for a in alerts_store if a.get("is_active", True)])
        
        return {
            "master_dashboard_machines_total": len(machines_store),
            "master_dashboard_metrics_total": total_metrics,
            "master_dashboard_alerts_active": active_alerts,
            "master_dashboard_websocket_connections": websocket_manager.get_connection_count(),
            "master_dashboard_system_cpu_percent": psutil.cpu_percent(),
            "master_dashboard_system_memory_percent": psutil.virtual_memory().percent,
            "master_dashboard_uptime_seconds": (datetime.now() - datetime.now()).total_seconds()
        }
    except Exception as e:
        return {"error": str(e)}