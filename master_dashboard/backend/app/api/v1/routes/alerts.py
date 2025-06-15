from fastapi import APIRouter, HTTPException, Request
from typing import List
import uuid
from datetime import datetime

from app.schemas.alert import AlertResponse, AlertCreate, AlertUpdate

router = APIRouter()

@router.get("/active", response_model=List[AlertResponse])
async def get_active_alerts(request: Request):
    """Get all active alerts"""
    alerts_store = request.app.state.alerts_store
    return [alert for alert in alerts_store if alert.get("is_active", True)]

@router.get("/", response_model=List[AlertResponse])
async def get_all_alerts(request: Request):
    """Get all alerts"""
    alerts_store = request.app.state.alerts_store
    return alerts_store

@router.get("/{machine_id}", response_model=List[AlertResponse])
async def get_machine_alerts(machine_id: str, request: Request):
    """Get alerts for a specific machine"""
    machines_store = request.app.state.machines_store
    alerts_store = request.app.state.alerts_store
    
    if machine_id not in machines_store:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    return [alert for alert in alerts_store if alert.get("machine_id") == machine_id]

@router.post("/", response_model=AlertResponse)
async def create_alert(alert: AlertCreate, request: Request):
    """Create a new alert"""
    machines_store = request.app.state.machines_store
    alerts_store = request.app.state.alerts_store
    websocket_manager = request.app.state.websocket_manager
    
    if alert.machine_id not in machines_store:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    alert_id = f"alert-{str(uuid.uuid4())[:8]}"
    alert_data = {
        "id": alert_id,
        **alert.dict(),
        "created_at": datetime.now().isoformat(),
        "resolved_at": None,
        "is_active": True
    }
    
    alerts_store.append(alert_data)
    
    # Broadcast the new alert to all connected clients
    await websocket_manager.broadcast_json({
        "type": "alert_created",
        "alert": alert_data
    })
    
    return alert_data

@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(alert_id: str, alert: AlertUpdate, request: Request):
    """Update an alert"""
    alerts_store = request.app.state.alerts_store
    websocket_manager = request.app.state.websocket_manager
    
    alert_index = None
    for i, stored_alert in enumerate(alerts_store):
        if stored_alert.get("id") == alert_id:
            alert_index = i
            break
    
    if alert_index is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert_data = alerts_store[alert_index].copy()
    update_data = alert.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "resolved_at" and value:
            alert_data[field] = value.isoformat() if hasattr(value, 'isoformat') else value
        else:
            alert_data[field] = value
    
    alerts_store[alert_index] = alert_data
    
    # Broadcast the alert update
    await websocket_manager.broadcast_json({
        "type": "alert_updated",
        "alert": alert_data
    })
    
    return alert_data

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, request: Request):
    """Delete an alert"""
    alerts_store = request.app.state.alerts_store
    
    alert_index = None
    for i, stored_alert in enumerate(alerts_store):
        if stored_alert.get("id") == alert_id:
            alert_index = i
            break
    
    if alert_index is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    del alerts_store[alert_index]
    
    return {"message": "Alert deleted successfully"}