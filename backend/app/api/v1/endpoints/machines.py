# backend/app/api/v1/endpoints/machines.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, create_api_key
from app.models.machine import Machine as MachineModel, ConnectionStatus
from app.models.hardware import HardwareComponent as HardwareModel
from app.schemas.machine import (
    Machine, MachineCreate, MachineUpdate, MachineList, 
    MachineRegistration, MachineStats
)

router = APIRouter()

@router.get("/", response_model=MachineList)
async def list_machines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ConnectionStatus] = None,
    machine_type: Optional[str] = None,
    group_name: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of machines with filtering and pagination"""
    query = db.query(MachineModel)
    
    # Apply filters
    if status:
        query = query.filter(MachineModel.status == status)
    if machine_type:
        query = query.filter(MachineModel.machine_type == machine_type)
    if group_name:
        query = query.filter(MachineModel.group_name == group_name)
    if search:
        query = query.filter(
            or_(
                MachineModel.name.ilike(f"%{search}%"),
                MachineModel.hostname.ilike(f"%{search}%"),
                MachineModel.ip_address.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    machines = query.offset(skip).limit(limit).all()
    
    return MachineList(
        machines=machines,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.post("/", response_model=Machine)
async def create_machine(
    machine: MachineCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new machine"""
    # Check if machine with same IP already exists
    existing = db.query(MachineModel).filter(
        and_(
            MachineModel.ip_address == machine.ip_address,
            MachineModel.port == machine.port
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Machine with IP {machine.ip_address}:{machine.port} already exists"
        )
    
    # Create API key for the machine
    machine_id = str(uuid.uuid4())
    api_key = create_api_key(machine_id, "agent")
    
    db_machine = MachineModel(
        id=machine_id,
        api_key=api_key,
        **machine.dict()
    )
    
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    
    return db_machine

@router.get("/{machine_id}", response_model=Machine)
async def get_machine(
    machine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get machine by ID"""
    machine = db.query(MachineModel).filter(MachineModel.id == machine_id).first()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    return machine

@router.put("/{machine_id}", response_model=Machine)
async def update_machine(
    machine_id: uuid.UUID,
    machine_update: MachineUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update machine"""
    machine = db.query(MachineModel).filter(MachineModel.id == machine_id).first()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    update_data = machine_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(machine, field, value)
    
    machine.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(machine)
    
    return machine

@router.delete("/{machine_id}")
async def delete_machine(
    machine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete machine"""
    machine = db.query(MachineModel).filter(MachineModel.id == machine_id).first()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    # Delete associated hardware components
    db.query(HardwareModel).filter(HardwareModel.machine_id == machine_id).delete()
    
    # Delete machine
    db.delete(machine)
    db.commit()
    
    return {"message": "Machine deleted successfully"}

@router.post("/register", response_model=Machine)
async def register_machine(
    registration: MachineRegistration,
    db: Session = Depends(get_db)
):
    """Register a new machine from client agent"""
    machine_info = registration.machine_info
    hardware_info = registration.hardware_info
    
    # Check if machine already exists by IP
    existing = db.query(MachineModel).filter(
        MachineModel.ip_address == machine_info.get("ip_address")
    ).first()
    
    if existing:
        # Update existing machine
        existing.hardware_info = hardware_info
        existing.last_seen = datetime.utcnow()
        existing.status = ConnectionStatus.ONLINE
        existing.hostname = machine_info.get("hostname")
        existing.os_name = machine_info.get("os_name")
        existing.os_version = machine_info.get("os_version")
        existing.architecture = machine_info.get("architecture")
        
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new machine
    machine_id = str(uuid.uuid4())
    api_key = create_api_key(machine_id, "agent")
    
    db_machine = MachineModel(
        id=machine_id,
        name=machine_info.get("hostname", f"Machine-{machine_info.get('ip_address')}"),
        ip_address=machine_info.get("ip_address"),
        hostname=machine_info.get("hostname"),
        os_name=machine_info.get("os_name"),
        os_version=machine_info.get("os_version"),
        architecture=machine_info.get("architecture"),
        hardware_info=hardware_info,
        api_key=api_key,
        status=ConnectionStatus.ONLINE,
        last_seen=datetime.utcnow()
    )
    
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    
    return db_machine

@router.get("/{machine_id}/stats", response_model=MachineStats)
async def get_machine_stats(
    machine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get machine statistics"""
    machine = db.query(MachineModel).filter(MachineModel.id == machine_id).first()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    # Get latest metrics from hardware_info or return defaults
    hardware_info = machine.hardware_info or {}
    
    return MachineStats(
        machine_id=machine_id,
        cpu_usage=hardware_info.get("cpu_usage"),
        memory_usage=hardware_info.get("memory_usage"),
        disk_usage=hardware_info.get("disk_usage"),
        temperature=hardware_info.get("temperature"),
        uptime=hardware_info.get("uptime"),
        process_count=hardware_info.get("process_count"),
        last_update=machine.last_metrics_update
    )

@router.post("/{machine_id}/status")
async def update_machine_status(
    machine_id: uuid.UUID,
    status: ConnectionStatus,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update machine status"""
    machine = db.query(MachineModel).filter(MachineModel.id == machine_id).first()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    machine.status = status
    machine.updated_at = datetime.utcnow()
    if status == ConnectionStatus.ONLINE:
        machine.last_seen = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"Machine status updated to {status}"}