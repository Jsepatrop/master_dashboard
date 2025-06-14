from fastapi import WebSocket
from typing import List, Dict
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict] = {}
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_info[websocket] = {
            "connected_at": datetime.now(),
            "client_ip": websocket.client.host if websocket.client else "unknown"
        }
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_info:
            del self.connection_info[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
            
    async def broadcast(self, message: str):
        if not self.active_connections:
            return
            
        # Create a copy of connections to avoid modification during iteration
        connections_copy = self.active_connections.copy()
        disconnected = []
        
        for connection in connections_copy:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
                
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
            
    async def broadcast_json(self, data: dict):
        message = json.dumps(data)
        await self.broadcast(message)
        
    def get_connection_count(self) -> int:
        return len(self.active_connections)
        
    def get_connection_info(self) -> List[Dict]:
        return [
            {
                "client_ip": info["client_ip"],
                "connected_at": info["connected_at"].isoformat(),
                "duration": (datetime.now() - info["connected_at"]).total_seconds()
            }
            for info in self.connection_info.values()
        ]