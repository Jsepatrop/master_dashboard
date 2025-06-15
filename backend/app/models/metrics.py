# backend/app/models/metrics.py
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
from enum import Enum

from app.core.database import Base

class MetricType(str, Enum):
    CPU_USAGE = "cpu_usage"
    CPU_TEMPERATURE = "cpu_temperature"
    CPU_FREQUENCY = "cpu_frequency"
    MEMORY_USAGE = "memory_usage"
    MEMORY_AVAILABLE = "memory_available"
    GPU_USAGE = "gpu_usage"
    GPU_MEMORY = "gpu_memory"
    GPU_TEMPERATURE = "gpu_temperature"
    DISK_USAGE = "disk_usage"
    DISK_IO_READ = "disk_io_read"
    DISK_IO_WRITE = "disk_io_write"
    NETWORK_IO_SENT = "network_io_sent"
    NETWORK_IO_RECV = "network_io_recv"
    POWER_CONSUMPTION = "power_consumption"
    PROCESS_COUNT = "process_count"
    LOAD_AVERAGE = "load_average"
    UPTIME = "uptime"

class MetricData(Base):
    __tablename__ = "metrics"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    machine_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("machines.id"), nullable=False, index=True)
    
    # Metric identification
    metric_type = sa.Column(sa.Enum(MetricType), nullable=False, index=True)
    component_name = sa.Column(sa.String(100))  # e.g., "CPU0", "GPU0", "eth0", "/dev/sda1"
    
    # Metric data
    value = sa.Column(sa.Float, nullable=False)
    unit = sa.Column(sa.String(20))  # e.g., "%", "°C", "MB/s", "GB"
    
    # Timestamp
    timestamp = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Additional metadata
    metadata = sa.Column(JSONB, default={})
    
    # Indexes for efficient queries
    __table_args__ = (
        sa.Index('ix_metrics_machine_type_time', 'machine_id', 'metric_type', 'timestamp'),
        sa.Index('ix_metrics_time_desc', 'timestamp', postgresql_using='btree', postgresql_ops={'timestamp': 'DESC'}),
    )
    
    def __repr__(self):
        return f"<MetricData(machine_id={self.machine_id}, type='{self.metric_type}', value={self.value}, timestamp='{self.timestamp}')>"