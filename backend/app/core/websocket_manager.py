# backend/app/core/websocket_manager.py
import json
import logging
from typing import Dict, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        # Store active connections by client_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Store client types (dashboard, agent, etc.)
        self.client_types: Dict[str, str] = {}
        # Store last seen timestamps
        self.last_seen: Dict[str, datetime] = {}
        # Message queue for broadcasting
        self.message_queue: asyncio.Queue = asyncio.Queue()
        
    async def connect(self, websocket: WebSocket, client_type: str, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_types[client_id] = client_type
        self.last_seen[client_id] = datetime.utcnow()
        
        logger.info(f"Client {client_id} ({client_type}) connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
        # Notify other dashboard clients about new connection
        if client_type == "agent":
            await self.broadcast_to_dashboards({
                "type": "agent_connected",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            client_type = self.client_types.get(client_id, "unknown")
            del self.active_connections[client_id]
            del self.client_types[client_id]
            del self.last_seen[client_id]
            
            logger.info(f"Client {client_id} ({client_type}) disconnected. Total connections: {len(self.active_connections)}")
            
            # Notify dashboard clients about disconnection
            if client_type == "agent":
                asyncio.create_task(self.broadcast_to_dashboards({
                    "type": "agent_disconnected",
                    "client_id": client_id,
                    "timestamp": datetime.utcnow().isoformat()
                }))
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            if client_id in self.active_connections:
                self.disconnect(self.active_connections[client_id], client_id)
    
    async def broadcast_to_dashboards(self, message: Dict[str, Any]):
        """Broadcast message only to dashboard clients"""
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            if self.client_types.get(client_id) == "dashboard":
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to dashboard {client_id}: {e}")
                    disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            if client_id in self.active_connections:
                self.disconnect(self.active_connections[client_id], client_id)
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                self.disconnect(self.active_connections[client_id], client_id)
    
    async def handle_message(self, websocket: WebSocket, client_type: str, client_id: str, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        try:
            self.last_seen[client_id] = datetime.utcnow()
            message_type = data.get("type")
            
            if message_type == "ping":
                await self.send_personal_message({"type": "pong", "timestamp": datetime.utcnow().isoformat()}, websocket)
            
            elif message_type == "metrics_update" and client_type == "agent":
                # Forward metrics to dashboard clients
                await self.broadcast_to_dashboards({
                    "type": "metrics_update",
                    "client_id": client_id,
                    "data": data.get("data", {}),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif message_type == "machine_registration" and client_type == "agent":
                # Handle machine registration
                await self.broadcast_to_dashboards({
                    "type": "machine_registered",
                    "client_id": client_id,
                    "machine_info": data.get("machine_info", {}),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            else:
                logger.warning(f"Unknown message type '{message_type}' from {client_id}")
                
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        stats = {
            "total_connections": len(self.active_connections),
            "dashboard_clients": len([c for c in self.client_types.values() if c == "dashboard"]),
            "agent_clients": len([c for c in self.client_types.values() if c == "agent"]),
            "simulator_clients": len([c for c in self.client_types.values() if c == "simulator"]),
            "connected_clients": list(self.active_connections.keys())
        }
        return stats