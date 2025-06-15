from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List
import uvicorn

from app.core.config import settings
from app.core.websocket_manager import WebSocketManager
from app.api.v1.api import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize WebSocket manager
websocket_manager = WebSocketManager()

# In-memory storage for demo (replace with database in production)
machines_store: Dict = {}
metrics_store: Dict = {}
alerts_store: List = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Master Dashboard Backend...")
    
    # Initialize sample machines
    sample_machines = [
        {
            "id": "machine-001",
            "name": "Web Server Alpha",
            "type": "WEB_SERVER",
            "status": "ONLINE",
            "position": {"x": -2, "y": 0, "z": 0, "rotation_x": 0, "rotation_y": 0, "rotation_z": 0},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "machine-002", 
            "name": "Database Cluster",
            "type": "DATABASE_SERVER",
            "status": "ONLINE",
            "position": {"x": 0, "y": 0, "z": 0, "rotation_x": 0, "rotation_y": 0, "rotation_z": 0},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "machine-003",
            "name": "Load Balancer",
            "type": "LOAD_BALANCER", 
            "status": "ONLINE",
            "position": {"x": 2, "y": 0, "z": 0, "rotation_x": 0, "rotation_y": 0, "rotation_z": 0},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "machine-004",
            "name": "Cache Server",
            "type": "CACHE_SERVER",
            "status": "ONLINE", 
            "position": {"x": -1, "y": 0, "z": 2, "rotation_x": 0, "rotation_y": 0, "rotation_z": 0},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "machine-005",
            "name": "App Server Beta",
            "type": "APPLICATION_SERVER",
            "status": "ONLINE",
            "position": {"x": 1, "y": 0, "z": 2, "rotation_x": 0, "rotation_y": 0, "rotation_z": 0},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    for machine in sample_machines:
        machines_store[machine["id"]] = machine
        metrics_store[machine["id"]] = []
    
    logger.info(f"Initialized {len(sample_machines)} sample machines")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Master Dashboard Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Master Dashboard - 3D Infrastructure Monitoring System",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Master Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws/metrics")
async def websocket_metrics_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
            logger.info(f"Received WebSocket message: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

@app.websocket("/ws/data")
async def websocket_data_endpoint(websocket: WebSocket):
    """WebSocket endpoint for data simulator"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "metrics_batch":
                    # Store metrics and broadcast to all clients
                    metrics_data = message.get("data", [])
                    for metric in metrics_data:
                        machine_id = metric.get("machine_id")
                        if machine_id in metrics_store:
                            metrics_store[machine_id].append(metric)
                            # Keep only last 100 metrics per machine
                            if len(metrics_store[machine_id]) > 100:
                                metrics_store[machine_id] = metrics_store[machine_id][-100:]
                    
                    # Broadcast to all connected clients
                    await websocket_manager.broadcast(data)
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("Data simulator disconnected")

# Make stores accessible to routes
app.state.machines_store = machines_store
app.state.metrics_store = metrics_store
app.state.alerts_store = alerts_store
app.state.websocket_manager = websocket_manager

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )