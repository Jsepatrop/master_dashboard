# backend/app/core/config.py
import os
from typing import List, Optional
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Master Dashboard Revolutionary"
    
    # Database Settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://dashboard:password123@localhost:5432/master_dashboard"
    )
    
    # Redis Settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security Settings
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "your-super-secret-key-change-in-production-master-dashboard-revolutionary"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://localhost:3000",
        "https://localhost:5173",
        "https://localhost:8080",
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 1000
    
    # Metrics Settings
    METRICS_RETENTION_DAYS: int = 30
    METRICS_AGGREGATION_INTERVAL: int = 5  # seconds
    
    # Simulator Settings
    SIMULATOR_ENABLED: bool = True
    SIMULATOR_MACHINE_COUNT: int = 8
    SIMULATOR_UPDATE_INTERVAL: int = 5  # seconds
    
    # Alert Settings
    ALERT_CHECK_INTERVAL: int = 10  # seconds
    DEFAULT_CPU_THRESHOLD: float = 80.0
    DEFAULT_MEMORY_THRESHOLD: float = 85.0
    DEFAULT_TEMPERATURE_THRESHOLD: float = 75.0
    
    # External Services
    INFLUXDB_URL: Optional[str] = None
    INFLUXDB_TOKEN: Optional[str] = None
    INFLUXDB_ORG: Optional[str] = None
    INFLUXDB_BUCKET: Optional[str] = None
    
    MQTT_BROKER: Optional[str] = None
    MQTT_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()