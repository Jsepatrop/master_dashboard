# backend/app/main.py
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.core.config import settings
from app.core.database import database, engine, metadata
from app.core.websocket_manager import WebSocketManager
from app.api.v1.api import api_router
from app.services.hardware_simulator import HardwareSimulator
from app.services.metrics_processor import MetricsProcessor
from app.services.alert_manager import AlertManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
websocket_manager = WebSocketManager()
hardware_simulator = HardwareSimulator()
metrics_processor = MetricsProcessor()
alert_manager = AlertManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Master Dashboard Revolutionary...")
    
    # Initialize database
    await database.connect()
    metadata.create_all(engine)
    logger.info("Database connected and tables created")
    
    # Start hardware simulator for autonomous operation
    await hardware_simulator.start()
    logger.info("Hardware simulator started")
    
    # Start metrics processor
    await metrics_processor.start()
    logger.info("Metrics processor started")
    
    # Start alert manager
    await alert_manager.start()
    logger.info("Alert manager started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Master Dashboard Revolutionary...")
    await hardware_simulator.stop()
    await metrics_processor.stop()
    await alert_manager.stop()
    await database.disconnect()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Revolutionary 3D Infrastructure Monitoring Dashboard",
    version="3.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "Master Dashboard Revolutionary v3.0",
        "status": "operational",
        "simulator_active": hardware_simulator.is_running,
        "connected_clients": len(websocket_manager.active_connections),
        "version": "3.0.0"
    }

@app.websocket("/ws/{client_type}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_type: str, client_id: str):
    """WebSocket endpoint for real-time communication"""
    await websocket_manager.connect(websocket, client_type, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            await websocket_manager.handle_message(websocket, client_type, client_id, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        websocket_manager.disconnect(websocket, client_id)

# Make global instances available to other modules
app.state.websocket_manager = websocket_manager
app.state.hardware_simulator = hardware_simulator
app.state.metrics_processor = metrics_processor
app.state.alert_manager = alert_manager

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )