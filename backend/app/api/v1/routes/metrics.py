from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict, Any
import uuid
from datetime import datetime

from app.schemas.metrics import MetricResponse, MetricCreate

router = APIRouter()

@router.get("/latest", response_model=Dict[str, List[Dict[str, Any]]])
async def get_latest_metrics(request: Request):
    """Get latest metrics for all machines"""
    metrics_store = request.app.state.metrics_store
    
    latest_metrics = {}
    for machine_id, metrics_list in metrics_store.items():
        if metrics_list:
            # Get the latest metrics (last 4 entries for each machine)
            latest_metrics[machine_id] = metrics_list[-4:]
        else:
            latest_metrics[machine_id] = []
    
    return latest_metrics

@router.get("/{machine_id}", response_model=List[Dict[str, Any]])
async def get_machine_metrics(machine_id: str, request: Request, limit: int = 100):
    """Get metrics for a specific machine"""
    machines_store = request.app.state.machines_store
    metrics_store = request.app.state.metrics_store
    
    if machine_id not in machines_store:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    if machine_id not in metrics_store:
        return []
    
    metrics = metrics_store[machine_id]
    return metrics[-limit:] if len(metrics) > limit else metrics

@router.post("/{machine_id}", response_model=Dict[str, Any])
async def create_metric(machine_id: str, metric: MetricCreate, request: Request):
    """Create a new metric for a machine"""
    machines_store = request.app.state.machines_store
    metrics_store = request.app.state.metrics_store
    websocket_manager = request.app.state.websocket_manager
    
    if machine_id not in machines_store:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    metric_id = f"metric-{str(uuid.uuid4())[:8]}"
    metric_data = {
        "id": metric_id,
        **metric.dict(),
        "timestamp": datetime.now().isoformat()
    }
    
    if machine_id not in metrics_store:
        metrics_store[machine_id] = []
    
    metrics_store[machine_id].append(metric_data)
    
    # Keep only last 100 metrics per machine
    if len(metrics_store[machine_id]) > 100:
        metrics_store[machine_id] = metrics_store[machine_id][-100:]
    
    # Broadcast the new metric to all connected clients
    await websocket_manager.broadcast_json({
        "type": "metric_update",
        "machine_id": machine_id,
        "metric": metric_data
    })
    
    return metric_data