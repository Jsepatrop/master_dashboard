# backend/app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import psutil
import platform

from app.core.database import get_db, database
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "service": "Master Dashboard Revolutionary"
    }

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with system information"""
    try:
        # Database connectivity test
        db_status = "healthy"
        try:
            db.execute("SELECT 1")
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # System information
        system_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
        
        # Resource usage
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resource_usage = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        }
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "3.0.0",
            "service": "Master Dashboard Revolutionary",
            "database_status": db_status,
            "system_info": system_info,
            "resource_usage": resource_usage,
            "uptime": datetime.utcnow().isoformat()  # Simplified uptime
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Check database connection
        await database.execute("SELECT 1")
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics")
async def metrics_endpoint():
    """Prometheus-style metrics endpoint"""
    try:
        # Basic system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = [
            f"# HELP system_cpu_percent Current CPU usage percentage",
            f"# TYPE system_cpu_percent gauge",
            f"system_cpu_percent {cpu_percent}",
            f"",
            f"# HELP system_memory_usage_percent Current memory usage percentage",
            f"# TYPE system_memory_usage_percent gauge", 
            f"system_memory_usage_percent {memory.percent}",
            f"",
            f"# HELP system_disk_usage_percent Current disk usage percentage",
            f"# TYPE system_disk_usage_percent gauge",
            f"system_disk_usage_percent {(disk.used / disk.total) * 100}",
            f"",
            f"# HELP system_memory_total_bytes Total system memory in bytes",
            f"# TYPE system_memory_total_bytes gauge",
            f"system_memory_total_bytes {memory.total}",
            f"",
            f"# HELP system_memory_available_bytes Available system memory in bytes",
            f"# TYPE system_memory_available_bytes gauge",
            f"system_memory_available_bytes {memory.available}",
        ]
        
        return "\n".join(metrics)
        
    except Exception as e:
        return f"# Error collecting metrics: {str(e)}"