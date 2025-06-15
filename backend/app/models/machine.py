# backend/app/models/machine.py
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
from enum import Enum

from app.core.database import Base

class MachineType(str, Enum):
    SERVER = "server"
    WORKSTATION = "workstation"
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    EMBEDDED = "embedded"

class ConnectionStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"

class Machine(Base):
    __tablename__ = "machines"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = sa.Column(sa.String(255), nullable=False, index=True)
    ip_address = sa.Column(sa.String(45), nullable=False, index=True)  # IPv4 or IPv6
    port = sa.Column(sa.Integer, default=8001)
    machine_type = sa.Column(sa.Enum(MachineType), default=MachineType.SERVER)
    status = sa.Column(sa.Enum(ConnectionStatus), default=ConnectionStatus.UNKNOWN)
    
    # Machine information
    hostname = sa.Column(sa.String(255))
    os_name = sa.Column(sa.String(100))
    os_version = sa.Column(sa.String(100))
    architecture = sa.Column(sa.String(50))
    
    # Hardware information (JSON)
    hardware_info = sa.Column(JSONB, default={})
    
    # Configuration and settings
    configuration = sa.Column(JSONB, default={})
    
    # Monitoring settings
    monitoring_enabled = sa.Column(sa.Boolean, default=True)
    collection_interval = sa.Column(sa.Integer, default=5)  # seconds
    
    # Alert thresholds
    cpu_threshold = sa.Column(sa.Float, default=80.0)
    memory_threshold = sa.Column(sa.Float, default=85.0)
    temperature_threshold = sa.Column(sa.Float, default=75.0)
    disk_threshold = sa.Column(sa.Float, default=90.0)
    
    # Timestamps
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = sa.Column(sa.DateTime)
    last_metrics_update = sa.Column(sa.DateTime)
    
    # Tags and groups
    tags = sa.Column(JSONB, default=[])
    group_name = sa.Column(sa.String(100), default="default")
    
    # 3D visualization data
    position_3d = sa.Column(JSONB, default={"x": 0, "y": 0, "z": 0})
    motherboard_model = sa.Column(sa.String(100), default="generic")
    
    # API key for client authentication
    api_key = sa.Column(sa.String(255), unique=True, index=True)
    
    def __repr__(self):
        return f"<Machine(id={self.id}, name='{self.name}', ip='{self.ip_address}', status='{self.status}')>"