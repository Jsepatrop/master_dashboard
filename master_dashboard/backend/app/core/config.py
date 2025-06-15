from pydantic_settings import BaseSettings
from typing import List, Optional
import secrets
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Master Dashboard API"
    API_V1_STR: str = "/api/v1"
    
    # CORS settings - Secure for production
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://frontend:3000",
        "http://frontend:80",
        "https://localhost:3000"
        # Remove "*" wildcard for security
    ]
    
    # Database settings
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # Security settings - Generate secure secret key
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Monitoring settings
    LOG_LEVEL: str = "INFO"
    
    # WebSocket settings
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    MAX_WEBSOCKET_CONNECTIONS: int = 100
    
    # Security headers
    ENABLE_SECURITY_HEADERS: bool = True
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()