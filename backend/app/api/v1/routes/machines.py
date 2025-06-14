from fastapi import APIRouter, HTTPException, Request
from typing import List
import uuid
from datetime import datetime

from app.schemas.machine import MachineResponse, MachineCreate, MachineUpdate

router = APIRouter()

@router.get("/", response_model=List[MachineResponse])
async def get_machines(request: Request):
    """Get all machines"""
    machines_store = request.app.state.machines_store
    return list(machines_store.values())

@router.get("/{machine_id}", response_model=MachineResponse)
async def get_machine(machine_id: str, request: Request):
    """Get a specific machine by ID"""
    machines_store = request.app.state.machines_store
    if machine_id not in machines_store:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machines_store[machine_id]

@router.post("/", response_model=MachineResponse)
async def create_machine(machine: MachineCreate, request: Request):
    """Create a new machine"""
    machines_store = request.app.state.machines_store
    
    machine_id = f"machine-{str(uuid.uuid4())[:8]}"
    machine_data = {
        "id": machine_id,
        **machine.dict(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    machines_store[machine_id] = machine_data
    
    # Initialize empty metrics for this machine
    metrics_store = request.app.state.metrics_store
    metrics_store[machine_id] = []
    
    return machine_data

@router.put("/{machine_id}", response_model=MachineResponse)
async def update_machine(machine_id: str, machine: MachineUpdate, request: Request):
    """Update a machine"""
    machines_store = request.app.state.machines_store
    
    if machine_id not in machines_store:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    machine_data = machines_store[machine_id].copy()
    update_data = machine.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        machine_data[field] = value
    
    machine_data["updated_at"] = datetime.now().isoformat()
    machines_store[machine_id] = machine_data
    
    return machine_data

@router.delete("/{machine_id}")
async def delete_machine(machine_id: str, request: Request):
    """Delete a machine"""
    machines_store = request.app.state.machines_store
    metrics_store = request.app.state.metrics_store
    
    if machine_id not in machines_store:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    del machines_store[machine_id]
    if machine_id in metrics_store:
        del metrics_store[machine_id]
    
    return {"message": "Machine deleted successfully"}