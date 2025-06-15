# backend/app/models/configuration.py
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.core.database import Base

class SystemConfiguration(Base):
    __tablename__ = "system_configuration"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Configuration sections
    influxdb_config = sa.Column(JSONB, default={
        "enabled": False,
        "url": "",
        "token": "",
        "org": "",
        "bucket": "",
        "timeout": 30
    })
    
    mqtt_config = sa.Column(JSONB, default={
        "enabled": False,
        "broker": "",
        "port": 1883,
        "username": "",
        "password": "",
        "topic_prefix": "master_dashboard",
        "qos": 1,
        "keepalive": 60
    })
    
    alert_config = sa.Column(JSONB, default={
        "email_enabled": False,
        "smtp_host": "",
        "smtp_port": 587,
        "smtp_username": "",
        "smtp_password": "",
        "smtp_tls": True,
        "from_email": "",
        "to_emails": [],
        "slack_enabled": False,
        "slack_webhook": "",
        "webhook_enabled": False,
        "webhook_url": "",
        "webhook_headers": {}
    })
    
    ui_config = sa.Column(JSONB, default={
        "theme": "cyberpunk",
        "refresh_interval": 5,
        "max_machines_display": 50,
        "enable_3d": True,
        "enable_animations": True,
        "enable_sound_alerts": True,
        "dashboard_title": "Master Dashboard Revolutionary",
        "show_fps": False,
        "auto_layout": True
    })
    
    monitoring_config = sa.Column(JSONB, default={
        "default_collection_interval": 5,
        "metrics_retention_days": 30,
        "enable_auto_discovery": True,
        "max_concurrent_connections": 1000,
        "websocket_heartbeat_interval": 30,
        "alert_evaluation_interval": 10
    })
    
    security_config = sa.Column(JSONB, default={
        "enable_authentication": True,
        "session_timeout_minutes": 60,
        "max_login_attempts": 5,
        "lockout_duration_minutes": 30,
        "password_min_length": 8,
        "require_https": False,
        "enable_audit_logs": True
    })
    
    # Metadata
    version = sa.Column(sa.String(20), default="3.0.0")
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = sa.Column(sa.String(100), default="system")
    
    # Backup and restore
    backup_enabled = sa.Column(sa.Boolean, default=True)
    last_backup_at = sa.Column(sa.DateTime)
    
    def __repr__(self):
        return f"<SystemConfiguration(id={self.id}, version='{self.version}', updated_at='{self.updated_at}')>"