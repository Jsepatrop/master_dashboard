from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class MachineType(str, Enum):
    WEB_SERVER = "WEB_SERVER"
    DATABASE_SERVER = "DATABASE_SERVER"
    APPLICATION_SERVER = "APPLICATION_SERVER"
    LOAD_BALANCER = "LOAD_BALANCER"
    CACHE_SERVER = "CACHE_SERVER"

class MachineStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"
    ERROR = "ERROR"

class Position3D(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0

class Machine(BaseModel):
    id: str = Field(..., description="Unique machine identifier")
    name: str = Field(..., description="Human-readable machine name")
    type: MachineType = Field(..., description="Type of machine")
    status: MachineStatus = Field(default=MachineStatus.ONLINE, description="Current machine status")
    position: Position3D = Field(default_factory=Position3D, description="3D position in the scene")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }