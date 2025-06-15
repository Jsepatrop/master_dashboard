# backend/app/schemas/metrics.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from app.models.metrics import MetricType

class MetricDataBase(BaseModel):
    metric_type: MetricType
    component_name: Optional[str] = None
    value: float
    unit: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MetricDataCreate(MetricDataBase):
    machine_id: uuid.UUID
    timestamp: Optional[datetime] = None

class MetricData(MetricDataBase):
    id: uuid.UUID
    machine_id: uuid.UUID
    timestamp: datetime

    class Config:
        orm_mode = True

class MetricsList(BaseModel):
    metrics: List[MetricData]
    total: int
    page: int
    size: int

class MetricsQuery(BaseModel):
    machine_ids: Optional[List[uuid.UUID]] = None
    metric_types: Optional[List[MetricType]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    component_names: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=100, ge=1, le=1000)

class MetricsExport(BaseModel):
    format: str = Field(..., regex="^(json|csv|xlsx)$")
    query: MetricsQuery
    include_metadata: bool = True

class MetricsBatch(BaseModel):
    machine_id: uuid.UUID
    metrics: List[MetricDataBase]
    timestamp: Optional[datetime] = None

class RealTimeMetrics(BaseModel):
    machine_id: uuid.UUID
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    gpu_usage: Optional[float] = None
    temperature: Optional[float] = None
    network_io: Optional[Dict[str, float]] = None
    disk_io: Optional[Dict[str, float]] = None
    timestamp: datetime