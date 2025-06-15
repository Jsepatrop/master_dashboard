from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class MetricType(str, Enum):
    CPU_USAGE = "CPU_USAGE"
    MEMORY_USAGE = "MEMORY_USAGE"
    DISK_USAGE = "DISK_USAGE"
    NETWORK_THROUGHPUT = "NETWORK_THROUGHPUT"

class Metric(BaseModel):
    id: str = Field(..., description="Unique metric identifier")
    machine_id: str = Field(..., description="Machine this metric belongs to")
    metric_type: MetricType = Field(..., description="Type of metric")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    timestamp: datetime = Field(default_factory=datetime.now, description="Metric timestamp")
    threshold_warning: Optional[float] = Field(None, description="Warning threshold")
    threshold_critical: Optional[float] = Field(None, description="Critical threshold")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }