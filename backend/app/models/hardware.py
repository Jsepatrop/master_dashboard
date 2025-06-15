# backend/app/models/hardware.py
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
from enum import Enum

from app.core.database import Base

class ComponentType(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    RAM = "ram"
    STORAGE = "storage"
    NETWORK = "network"
    MOTHERBOARD = "motherboard"
    PSU = "psu"
    COOLING = "cooling"
    TPU = "tpu"

class ComponentStatus(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

class HardwareComponent(Base):
    __tablename__ = "hardware_components"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    machine_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("machines.id"), nullable=False, index=True)
    
    # Component identification
    component_type = sa.Column(sa.Enum(ComponentType), nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    model = sa.Column(sa.String(255))
    manufacturer = sa.Column(sa.String(100))
    serial_number = sa.Column(sa.String(100))
    
    # Component specifications
    specifications = sa.Column(JSONB, default={})
    
    # Status and health
    status = sa.Column(sa.Enum(ComponentStatus), default=ComponentStatus.UNKNOWN)
    health_percentage = sa.Column(sa.Float, default=100.0)
    
    # Current metrics
    temperature = sa.Column(sa.Float)
    utilization = sa.Column(sa.Float)  # Usage percentage
    power_consumption = sa.Column(sa.Float)  # Watts
    
    # 3D visualization data
    position_3d = sa.Column(JSONB, default={"x": 0, "y": 0, "z": 0})
    rotation_3d = sa.Column(JSONB, default={"x": 0, "y": 0, "z": 0})
    scale_3d = sa.Column(JSONB, default={"x": 1, "y": 1, "z": 1})
    color_override = sa.Column(sa.String(7))  # Hex color code
    
    # Component-specific data
    # CPU
    cores = sa.Column(sa.Integer)
    threads = sa.Column(sa.Integer)
    base_frequency = sa.Column(sa.Float)  # GHz
    max_frequency = sa.Column(sa.Float)  # GHz
    cache_size = sa.Column(sa.Integer)  # MB
    
    # GPU
    memory_total = sa.Column(sa.Integer)  # MB
    memory_used = sa.Column(sa.Integer)  # MB
    gpu_utilization = sa.Column(sa.Float)  # %
    memory_utilization = sa.Column(sa.Float)  # %
    
    # RAM
    capacity = sa.Column(sa.Integer)  # MB
    speed = sa.Column(sa.Integer)  # MHz
    slot_number = sa.Column(sa.Integer)
    
    # Storage
    total_space = sa.Column(sa.Integer)  # MB
    used_space = sa.Column(sa.Integer)  # MB
    read_speed = sa.Column(sa.Float)  # MB/s
    write_speed = sa.Column(sa.Float)  # MB/s
    smart_status = sa.Column(sa.String(20))
    
    # Network
    interface_name = sa.Column(sa.String(50))
    mac_address = sa.Column(sa.String(17))
    speed = sa.Column(sa.Integer)  # Mbps
    bytes_sent = sa.Column(sa.BigInteger)
    bytes_recv = sa.Column(sa.BigInteger)
    
    # Timestamps
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<HardwareComponent(id={self.id}, type='{self.component_type}', name='{self.name}', machine_id={self.machine_id})>"