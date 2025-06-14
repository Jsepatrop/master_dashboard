from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.machine import MachineType, MachineStatus, Position3D

class MachineBase(BaseModel):
    name: str = Field(..., description="Human-readable machine name")
    type: MachineType = Field(..., description="Type of machine")
    status: MachineStatus = Field(default=MachineStatus.ONLINE, description="Current machine status")
    position: Position3D = Field(default_factory=Position3D, description="3D position in the scene")

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[MachineType] = None
    status: Optional[MachineStatus] = None
    position: Optional[Position3D] = None

class MachineResponse(MachineBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }