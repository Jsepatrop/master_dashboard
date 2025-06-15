# backend/app/schemas/hardware.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from app.models.hardware import ComponentType, ComponentStatus

class HardwareComponentBase(BaseModel):
    component_type: ComponentType
    name: str = Field(..., min_length=1, max_length=255)
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    specifications: Dict[str, Any] = Field(default_factory=dict)
    status: ComponentStatus = ComponentStatus.UNKNOWN
    health_percentage: float = Field(default=100.0, ge=0, le=100)
    temperature: Optional[float] = None
    utilization: Optional[float] = Field(None, ge=0, le=100)
    power_consumption: Optional[float] = None
    position_3d: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    rotation_3d: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    scale_3d: Dict[str, float] = Field(default_factory=lambda: {"x": 1, "y": 1, "z": 1})
    color_override: Optional[str] = Field(None, regex="^#[0-9a-fA-F]{6}$")

class HardwareComponentCreate(HardwareComponentBase):
    machine_id: uuid.UUID

class HardwareComponentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    status: Optional[ComponentStatus] = None
    health_percentage: Optional[float] = Field(None, ge=0, le=100)
    temperature: Optional[float] = None
    utilization: Optional[float] = Field(None, ge=0, le=100)
    power_consumption: Optional[float] = None
    position_3d: Optional[Dict[str, float]] = None
    rotation_3d: Optional[Dict[str, float]] = None
    scale_3d: Optional[Dict[str, float]] = None
    color_override: Optional[str] = Field(None, regex="^#[0-9a-fA-F]{6}$")

class HardwareComponent(HardwareComponentBase):
    id: uuid.UUID
    machine_id: uuid.UUID
    cores: Optional[int] = None
    threads: Optional[int] = None
    base_frequency: Optional[float] = None
    max_frequency: Optional[float] = None
    cache_size: Optional[int] = None
    memory_total: Optional[int] = None
    memory_used: Optional[int] = None
    gpu_utilization: Optional[float] = None
    memory_utilization: Optional[float] = None
    capacity: Optional[int] = None
    speed: Optional[int] = None
    slot_number: Optional[int] = None
    total_space: Optional[int] = None
    used_space: Optional[int] = None
    read_speed: Optional[float] = None
    write_speed: Optional[float] = None
    smart_status: Optional[str] = None
    interface_name: Optional[str] = None
    mac_address: Optional[str] = None
    bytes_sent: Optional[int] = None
    bytes_recv: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    last_seen: datetime

    class Config:
        orm_mode = True

class HardwareComponentList(BaseModel):
    components: List[HardwareComponent]
    total: int
    page: int
    size: int

class CPUInfo(BaseModel):
    name: str
    cores: int
    threads: int
    base_frequency: float
    max_frequency: float
    cache_size: int
    architecture: str
    manufacturer: str

class GPUInfo(BaseModel):
    name: str
    memory_total: int
    driver_version: Optional[str] = None
    manufacturer: str
    compute_capability: Optional[str] = None

class MemoryInfo(BaseModel):
    total: int
    available: int
    used: int
    percentage: float
    modules: List[Dict[str, Any]] = Field(default_factory=list)

class StorageInfo(BaseModel):
    device: str
    mountpoint: str
    filesystem: str
    total: int
    used: int
    free: int
    percentage: float

class NetworkInfo(BaseModel):
    interface: str
    ip_address: Optional[str] = None
    mac_address: str
    speed: Optional[int] = None
    status: str