"""
WebSocket client for Master Dashboard Agent
Handles real-time communication with the Master Dashboard server via WebSocket
"""
import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, Callable
import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode
import ssl

class WebSocketClient:
    """WebSocket client for real-time communication"""
    
    def __init__(self, url: str, machine_id: str, api_key: str, logger: logging.Logger):
        self.url = url
        self.machine_id = machine_id
        self.api_key = api_key
        self.logger = logger
        self.websocket = None
        self.connected = False
        self.reconnect_interval = 5
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
        self.heartbeat_interval = 30
        self.last_heartbeat = 0
        self.message_handlers = {}
        self.ssl_context = None
        
        # Setup SSL context for secure connections
        if url.startswith('wss://'):
            self.ssl_context = ssl.create_default_context()
    
    async def connect(self) -> bool:
        """Connect to the WebSocket server"""
        try:
            self.logger.info(f"Connecting to WebSocket server: {self.url}")
            
            # Prepare connection headers
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'X-Machine-ID': self.machine_id,
                'X-Agent-Version': '1.0.0'
            }
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                self.url,
                extra_headers=headers,
                ssl=self.ssl_context,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5
            )
            
            self.connected = True
            self.reconnect_attempts = 0
            self.logger.info("WebSocket connection established")
            
            # Send initial registration message
            await self._send_registration()
            
            # Start background tasks
            asyncio.create_task(self._heartbeat_loop())
            asyncio.create_task(self._message_handler())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.websocket and not self.websocket.closed:
            self.logger.info("Disconnecting from WebSocket server")
            self.connected = False
            await self.websocket.close()
            self.websocket = None
    
    async def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Send metrics data to server"""
        if not self.is_connected():
            self.logger.warning("Cannot send metrics: WebSocket not connected")
            return False
        
        try:
            message = {
                'type': 'metrics',
                'timestamp': time.time(),
                'machine_id': self.machine_id,
                'data': metrics
            }
            
            await self.websocket.send(json.dumps(message))
            self.logger.debug("Metrics sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send metrics: {e}")
            self.connected = False
            return False
    
    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """Send alert to server"""
        if not self.is_connected():
            self.logger.warning("Cannot send alert: WebSocket not connected")
            return False
        
        try:
            message = {
                'type': 'alert',
                'timestamp': time.time(),
                'machine_id': self.machine_id,
                'data': alert
            }
            
            await self.websocket.send(json.dumps(message))
            self.logger.info(f"Alert sent: {alert.get('level', 'unknown')} - {alert.get('message', 'no message')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
            self.connected = False
            return False
    
    async def send_status_update(self, status: Dict[str, Any]) -> bool:
        """Send status update to server"""
        if not self.is_connected():
            return False
        
        try:
            message = {
                'type': 'status',
                'timestamp': time.time(),
                'machine_id': self.machine_id,
                'data': status
            }
            
            await self.websocket.send(json.dumps(message))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send status update: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return (self.connected and 
                self.websocket and 
                not self.websocket.closed)
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types"""
        self.message_handlers[message_type] = handler
    
    async def _send_registration(self):
        """Send initial registration message"""
        try:
            registration = {
                'type': 'register',
                'timestamp': time.time(),
                'machine_id': self.machine_id,
                'data': {
                    'agent_version': '1.0.0',
                    'platform': {
                        'system': __import__('platform').system(),
                        'release': __import__('platform').release(),
                        'machine': __import__('platform').machine()
                    }
                }
            }
            
            await self.websocket.send(json.dumps(registration))
            self.logger.debug("Registration message sent")
            
        except Exception as e:
            self.logger.error(f"Failed to send registration: {e}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self.is_connected():
            try:
                current_time = time.time()
                if current_time - self.last_heartbeat >= self.heartbeat_interval:
                    heartbeat = {
                        'type': 'heartbeat',
                        'timestamp': current_time,
                        'machine_id': self.machine_id
                    }
                    
                    await self.websocket.send(json.dumps(heartbeat))
                    self.last_heartbeat = current_time
                    self.logger.debug("Heartbeat sent")
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Heartbeat failed: {e}")
                self.connected = False
                break
    
    async def _message_handler(self):
        """Handle incoming messages from server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get('type', 'unknown')
                    
                    self.logger.debug(f"Received message type: {message_type}")
                    
                    # Handle different message types
                    if message_type == 'command':
                        await self._handle_command(data)
                    elif message_type == 'config_update':
                        await self._handle_config_update(data)
                    elif message_type == 'ping':
                        await self._handle_ping(data)
                    elif message_type in self.message_handlers:
                        await self.message_handlers[message_type](data)
                    else:
                        self.logger.debug(f"Unhandled message type: {message_type}")
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON received: {e}")
                except Exception as e:
                    self.logger.error(f"Error handling message: {e}")
                    
        except ConnectionClosed:
            self.logger.warning("WebSocket connection closed by server")
            self.connected = False
        except Exception as e:
            self.logger.error(f"Message handler error: {e}")
            self.connected = False
    
    async def _handle_command(self, data: Dict[str, Any]):
        """Handle server commands"""
        command = data.get('data', {}).get('command')
        self.logger.info(f"Received command: {command}")
        
        # Respond to command
        response = {
            'type': 'command_response',
            'timestamp': time.time(),
            'machine_id': self.machine_id,
            'data': {
                'command': command,
                'status': 'acknowledged',
                'message': f"Command {command} received"
            }
        }
        
        try:
            await self.websocket.send(json.dumps(response))
        except Exception as e:
            self.logger.error(f"Failed to send command response: {e}")
    
    async def _handle_config_update(self, data: Dict[str, Any]):
        """Handle configuration updates from server"""
        config = data.get('data', {})
        self.logger.info("Received configuration update")
        
        # Apply configuration changes
        if 'heartbeat_interval' in config:
            self.heartbeat_interval = config['heartbeat_interval']
        
        if 'reconnect_interval' in config:
            self.reconnect_interval = config['reconnect_interval']
    
    async def _handle_ping(self, data: Dict[str, Any]):
        """Handle ping messages"""
        pong = {
            'type': 'pong',
            'timestamp': time.time(),
            'machine_id': self.machine_id,
            'data': data.get('data', {})
        }
        
        try:
            await self.websocket.send(json.dumps(pong))
        except Exception as e:
            self.logger.error(f"Failed to send pong: {e}")
    
    async def reconnect_loop(self):
        """Automatic reconnection loop"""
        while self.reconnect_attempts < self.max_reconnect_attempts:
            if not self.is_connected():
                self.reconnect_attempts += 1
                self.logger.info(f"Attempting to reconnect ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
                
                if await self.connect():
                    self.logger.info("Reconnection successful")
                    break
                else:
                    await asyncio.sleep(self.reconnect_interval)
            else:
                await asyncio.sleep(1)
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error("Max reconnection attempts reached")