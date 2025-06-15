# backend/app/models/alerts.py
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
from enum import Enum

from app.core.database import Base

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class ComparisonOperator(str, Enum):
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    EQUAL = "eq"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    NOT_EQUAL = "ne"

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    machine_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("machines.id"), nullable=False, index=True)
    component_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("hardware_components.id"), nullable=True)
    
    # Rule configuration
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text)
    metric_type = sa.Column(sa.String(50), nullable=False)
    threshold_value = sa.Column(sa.Float, nullable=False)
    comparison_operator = sa.Column(sa.Enum(ComparisonOperator), nullable=False)
    severity = sa.Column(sa.Enum(AlertSeverity), default=AlertSeverity.MEDIUM)
    
    # Rule status
    enabled = sa.Column(sa.Boolean, default=True)
    
    # Notification settings
    notification_channels = sa.Column(JSONB, default=[])  # ["email", "slack", "webhook"]
    notification_settings = sa.Column(JSONB, default={})
    
    # Timing settings
    evaluation_interval = sa.Column(sa.Integer, default=60)  # seconds
    cooldown_period = sa.Column(sa.Integer, default=300)  # seconds
    
    # Timestamps
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = sa.Column(sa.String(100), default="system")
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, name='{self.name}', severity='{self.severity}')>"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    rule_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("alert_rules.id"), nullable=False, index=True)
    machine_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("machines.id"), nullable=False, index=True)
    component_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("hardware_components.id"), nullable=True)
    
    # Alert details
    title = sa.Column(sa.String(255), nullable=False)
    message = sa.Column(sa.Text, nullable=False)
    severity = sa.Column(sa.Enum(AlertSeverity), nullable=False)
    status = sa.Column(sa.Enum(AlertStatus), default=AlertStatus.ACTIVE)
    
    # Metric data that triggered the alert
    metric_type = sa.Column(sa.String(50), nullable=False)
    current_value = sa.Column(sa.Float, nullable=False)
    threshold_value = sa.Column(sa.Float, nullable=False)
    
    # Additional context
    metadata = sa.Column(JSONB, default={})
    
    # Timestamps
    triggered_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    acknowledged_at = sa.Column(sa.DateTime)
    resolved_at = sa.Column(sa.DateTime)
    
    # User actions
    acknowledged_by = sa.Column(sa.String(100))
    resolved_by = sa.Column(sa.String(100))
    notes = sa.Column(sa.Text)
    
    def __repr__(self):
        return f"<Alert(id={self.id}, title='{self.title}', severity='{self.severity}', status='{self.status}')>"