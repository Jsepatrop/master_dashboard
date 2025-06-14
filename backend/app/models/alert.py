from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class AlertLevel(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class Alert(BaseModel):
    id: str = Field(..., description="Unique alert identifier")
    machine_id: str = Field(..., description="Machine this alert belongs to")
    metric_id: Optional[str] = Field(None, description="Metric that triggered the alert")
    level: AlertLevel = Field(..., description="Alert severity level")
    message: str = Field(..., description="Alert message")
    created_at: datetime = Field(default_factory=datetime.now, description="Alert creation timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Alert resolution timestamp")
    is_active: bool = Field(default=True, description="Whether the alert is still active")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }