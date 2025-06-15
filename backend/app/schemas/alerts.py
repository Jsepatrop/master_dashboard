# backend/app/schemas/alerts.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from app.models.alerts import AlertSeverity, AlertStatus, ComparisonOperator

class AlertRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    metric_type: str = Field(..., min_length=1, max_length=50)
    threshold_value: float
    comparison_operator: ComparisonOperator
    severity: AlertSeverity = AlertSeverity.MEDIUM
    enabled: bool = True
    notification_channels: List[str] = Field(default_factory=list)
    notification_settings: Dict[str, Any] = Field(default_factory=dict)
    evaluation_interval: int = Field(default=60, ge=10, le=3600)
    cooldown_period: int = Field(default=300, ge=60, le=7200)

class AlertRuleCreate(AlertRuleBase):
    machine_id: uuid.UUID
    component_id: Optional[uuid.UUID] = None

class AlertRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    threshold_value: Optional[float] = None
    comparison_operator: Optional[ComparisonOperator] = None
    severity: Optional[AlertSeverity] = None
    enabled: Optional[bool] = None
    notification_channels: Optional[List[str]] = None
    notification_settings: Optional[Dict[str, Any]] = None
    evaluation_interval: Optional[int] = Field(None, ge=10, le=3600)
    cooldown_period: Optional[int] = Field(None, ge=60, le=7200)

class AlertRule(AlertRuleBase):
    id: uuid.UUID
    machine_id: uuid.UUID
    component_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        orm_mode = True

class AlertBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    severity: AlertSeverity
    metric_type: str = Field(..., min_length=1, max_length=50)
    current_value: float
    threshold_value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AlertCreate(AlertBase):
    rule_id: uuid.UUID
    machine_id: uuid.UUID
    component_id: Optional[uuid.UUID] = None

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    notes: Optional[str] = None

class Alert(AlertBase):
    id: uuid.UUID
    rule_id: uuid.UUID
    machine_id: uuid.UUID
    component_id: Optional[uuid.UUID] = None
    status: AlertStatus
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        orm_mode = True

class AlertsList(BaseModel):
    alerts: List[Alert]
    total: int
    page: int
    size: int

class AlertSummary(BaseModel):
    total_alerts: int
    active_alerts: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int