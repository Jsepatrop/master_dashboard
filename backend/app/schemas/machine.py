# backend/app/schemas/machine.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

from app.models.machine import MachineType, ConnectionStatus

class MachineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., min_length=7, max_length=45)
    port: int = Field(default=8001, ge=1, le=65535)
    machine_type: MachineType = MachineType.SERVER
    hostname: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    architecture: Optional[str] = None
    configuration: Dict[str, Any] = Field(default_factory=dict)
    monitoring_enabled: bool = True
    collection_interval: int = Field(default=5, ge=1, le=300)
    cpu_threshold: float = Field(default=80.0, ge=0, le=100)
    memory_threshold: float = Field(default=85.0, ge=0, le=100)
    temperature_threshold: float = Field(default=75.0, ge=0, le=150)
    disk_threshold: float = Field(default=90.0, ge=0, le=100)
    tags: List[str] = Field(default_factory=list)
    group_name: str = "default"
    position_3d: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    motherboard_model: str = "generic"

    @validator('ip_address')
    def validate_ip_address(cls, v):
        import ipaddress
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError('Invalid IP address format')

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    port: Optional[int] = Field(None, ge=1, le=65535)
    machine_type: Optional[MachineType] = None
    configuration: Optional[Dict[str, Any]] = None
    monitoring_enabled: Optional[bool] = None
    collection_interval: Optional[int] = Field(None, ge=1, le=300)
    cpu_threshold: Optional[float] = Field(None, ge=0, le=100)
    memory_threshold: Optional[float] = Field(None, ge=0, le=100)
    temperature_threshold: Optional[float] = Field(None, ge=0, le=150)
    disk_threshold: Optional[float] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None
    group_name: Optional[str] = None
    position_3d: Optional[Dict[str, float]] = None
    motherboard_model: Optional[str] = None

class Machine(MachineBase):
    id: uuid.UUID
    status: ConnectionStatus
    hardware_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    last_seen: Optional[datetime] = None
    last_metrics_update: Optional[datetime] = None
    api_key: Optional[str] = None

    class Config:
        orm_mode = True

class MachineList(BaseModel):
    machines: List[Machine]
    total: int
    page: int
    size: int

class MachineRegistration(BaseModel):
    machine_info: Dict[str, Any]
    hardware_info: Dict[str, Any]
    client_version: str = "1.0.0"

class MachineStats(BaseModel):
    machine_id: uuid.UUID
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    temperature: Optional[float] = None
    uptime: Optional[int] = None
    process_count: Optional[int] = None
    last_update: Optional[datetime] = None