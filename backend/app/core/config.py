from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Master Dashboard API"
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://frontend:3000",
        "https://localhost:3000",
        "*"  # Allow all origins for development
    ]
    
    # Database settings (for future use)
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # Security settings
    SECRET_KEY: str = "master-dashboard-secret-key-change-in-production"
    
    # Monitoring settings
    LOG_LEVEL: str = "INFO"
    
    # WebSocket settings
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    MAX_WEBSOCKET_CONNECTIONS: int = 100
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()