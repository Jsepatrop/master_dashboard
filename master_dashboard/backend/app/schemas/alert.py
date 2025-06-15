from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.alert import AlertLevel

class AlertBase(BaseModel):
    machine_id: str = Field(..., description="Machine this alert belongs to")
    level: AlertLevel = Field(..., description="Alert severity level")
    message: str = Field(..., description="Alert message")
    metric_id: Optional[str] = Field(None, description="Metric that triggered the alert")

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    level: Optional[AlertLevel] = None
    message: Optional[str] = None
    is_active: Optional[bool] = None
    resolved_at: Optional[datetime] = None

class AlertResponse(AlertBase):
    id: str
    created_at: datetime
    resolved_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }