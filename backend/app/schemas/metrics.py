from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.metrics import MetricType

class MetricBase(BaseModel):
    machine_id: str = Field(..., description="Machine this metric belongs to")
    metric_type: MetricType = Field(..., description="Type of metric")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    threshold_warning: Optional[float] = Field(None, description="Warning threshold")
    threshold_critical: Optional[float] = Field(None, description="Critical threshold")

class MetricCreate(MetricBase):
    pass

class MetricUpdate(BaseModel):
    value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None

class MetricResponse(MetricBase):
    id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }