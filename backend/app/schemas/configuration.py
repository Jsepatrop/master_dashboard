# backend/app/schemas/configuration.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class InfluxDBConfig(BaseModel):
    enabled: bool = False
    url: str = ""
    token: str = ""
    org: str = ""
    bucket: str = ""
    timeout: int = Field(default=30, ge=5, le=300)

class MQTTConfig(BaseModel):
    enabled: bool = False
    broker: str = ""
    port: int = Field(default=1883, ge=1, le=65535)
    username: str = ""
    password: str = ""
    topic_prefix: str = "master_dashboard"
    qos: int = Field(default=1, ge=0, le=2)
    keepalive: int = Field(default=60, ge=10, le=300)

class AlertConfig(BaseModel):
    email_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_tls: bool = True
    from_email: str = ""
    to_emails: List[str] = Field(default_factory=list)
    slack_enabled: bool = False
    slack_webhook: str = ""
    webhook_enabled: bool = False
    webhook_url: str = ""
    webhook_headers: Dict[str, str] = Field(default_factory=dict)

class UIConfig(BaseModel):
    theme: str = Field(default="cyberpunk", regex="^(cyberpunk|corporate|minimal)$")
    refresh_interval: int = Field(default=5, ge=1, le=60)
    max_machines_display: int = Field(default=50, ge=10, le=1000)
    enable_3d: bool = True
    enable_animations: bool = True
    enable_sound_alerts: bool = True
    dashboard_title: str = "Master Dashboard Revolutionary"
    show_fps: bool = False
    auto_layout: bool = True

class MonitoringConfig(BaseModel):
    default_collection_interval: int = Field(default=5, ge=1, le=300)
    metrics_retention_days: int = Field(default=30, ge=1, le=365)
    enable_auto_discovery: bool = True
    max_concurrent_connections: int = Field(default=1000, ge=10, le=10000)
    websocket_heartbeat_interval: int = Field(default=30, ge=10, le=300)
    alert_evaluation_interval: int = Field(default=10, ge=5, le=300)

class SecurityConfig(BaseModel):
    enable_authentication: bool = True
    session_timeout_minutes: int = Field(default=60, ge=5, le=480)
    max_login_attempts: int = Field(default=5, ge=1, le=20)
    lockout_duration_minutes: int = Field(default=30, ge=5, le=1440)
    password_min_length: int = Field(default=8, ge=6, le=50)
    require_https: bool = False
    enable_audit_logs: bool = True

class SystemConfigurationBase(BaseModel):
    influxdb_config: InfluxDBConfig = Field(default_factory=InfluxDBConfig)
    mqtt_config: MQTTConfig = Field(default_factory=MQTTConfig)
    alert_config: AlertConfig = Field(default_factory=AlertConfig)
    ui_config: UIConfig = Field(default_factory=UIConfig)
    monitoring_config: MonitoringConfig = Field(default_factory=MonitoringConfig)
    security_config: SecurityConfig = Field(default_factory=SecurityConfig)

class SystemConfigurationUpdate(SystemConfigurationBase):
    pass

class SystemConfiguration(SystemConfigurationBase):
    id: uuid.UUID
    version: str
    updated_at: datetime
    updated_by: str
    backup_enabled: bool
    last_backup_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ConfigurationTest(BaseModel):
    service: str = Field(..., regex="^(influxdb|mqtt|email|slack|webhook)$")
    config: Dict[str, Any]

class ConfigurationTestResult(BaseModel):
    service: str
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None