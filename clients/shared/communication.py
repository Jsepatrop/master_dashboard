#!/usr/bin/env python3
"""
Dashboard Communication Module
Handles communication between agents and the Master Dashboard server
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin, urlparse

import aiohttp
import websockets
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class DashboardCommunicator:
    """Handles all communication with the Master Dashboard server"""
    
    def __init__(self, server_url: str, api_key: Optional[str] = None, timeout: int = 30):
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Parse server URL for WebSocket connection
        parsed_url = urlparse(server_url)
        ws_scheme = 'wss' if parsed_url.scheme == 'https' else 'ws'
        self.websocket_url = f"{ws_scheme}://{parsed_url.netloc}/ws/data"
        
        # Session management
        self._session = None
        self._websocket = None
        self._last_heartbeat = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            headers = {'User-Agent': 'MasterDashboard-Agent/1.0'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers
            )
    
    async def close(self):
        """Close all connections"""
        if self._websocket:
            try:
                await self._websocket.close()
            except Exception:
                pass
            self._websocket = None
            
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def test_connection(self) -> bool:
        """Test connection to the server"""
        try:
            await self._ensure_session()
            
            health_url = urljoin(self.server_url, '/api/v1/health')
            self.logger.debug(f"Testing connection to: {health_url}")
            
            async with self._session.get(health_url) as response:
                if response.status == 200:
                    data = await response.json()
                    self.logger.info(f"Server responded: {data}")
                    return True
                else:
                    self.logger.warning(f"Server returned status {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def register_machine(self, machine_info: Dict[str, Any]) -> bool:
        """Register machine with the server"""
        try:
            await self._ensure_session()
            
            register_url = urljoin(self.server_url, '/api/v1/machines')
            self.logger.debug(f"Registering machine at: {register_url}")
            
            async with self._session.post(register_url, json=machine_info) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    self.logger.info(f"Machine registered successfully: {result}")
                    return True
                elif response.status == 409:
                    self.logger.info("Machine already registered")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.error(f"Registration failed with status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Machine registration failed: {e}")
            return False
    
    async def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Send metrics to server via HTTP"""
        try:
            await self._ensure_session()
            
            metrics_url = urljoin(self.server_url, '/api/v1/metrics')
            
            async with self._session.post(metrics_url, json=metrics) as response:
                if response.status in [200, 201]:
                    self.logger.debug("Metrics sent successfully via HTTP")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.warning(f"Failed to send metrics via HTTP: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error sending metrics via HTTP: {e}")
            return False
    
    async def send_metrics_websocket(self, metrics: Dict[str, Any]) -> bool:
        """Send metrics to server via WebSocket"""
        try:
            if not self._websocket or self._websocket.closed:
                await self._connect_websocket()
                
            if self._websocket:
                message = json.dumps({
                    'type': 'metrics',
                    'data': metrics
                })
                await self._websocket.send(message)
                self.logger.debug("Metrics sent successfully via WebSocket")
                return True
            else:
                self.logger.warning("WebSocket not available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending metrics via WebSocket: {e}")
            self._websocket = None  # Reset connection on error
            return False
    
    async def _connect_websocket(self):
        """Establish WebSocket connection"""
        try:
            self.logger.debug(f"Connecting to WebSocket: {self.websocket_url}")
            
            extra_headers = {}
            if self.api_key:
                extra_headers['Authorization'] = f'Bearer {self.api_key}'
                
            self._websocket = await websockets.connect(
                self.websocket_url,
                extra_headers=extra_headers,
                ping_interval=30,
                ping_timeout=10
            )
            
            self.logger.info("WebSocket connection established")
            
        except Exception as e:
            self.logger.error(f"Failed to connect WebSocket: {e}")
            self._websocket = None
    
    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """Send alert to server"""
        try:
            await self._ensure_session()
            
            alerts_url = urljoin(self.server_url, '/api/v1/alerts')
            
            async with self._session.post(alerts_url, json=alert) as response:
                if response.status in [200, 201]:
                    self.logger.info("Alert sent successfully")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.warning(f"Failed to send alert: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
            return False
    
    async def get_server_config(self) -> Optional[Dict[str, Any]]:
        """Get configuration from server"""
        try:
            await self._ensure_session()
            
            config_url = urljoin(self.server_url, '/api/v1/config')
            
            async with self._session.get(config_url) as response:
                if response.status == 200:
                    config = await response.json()
                    self.logger.debug("Retrieved server configuration")
                    return config
                else:
                    self.logger.warning(f"Failed to get server config: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting server config: {e}")
            return None
    
    async def heartbeat(self) -> bool:
        """Send heartbeat to server"""
        try:
            current_time = time.time()
            
            # Throttle heartbeats to avoid spam
            if current_time - self._last_heartbeat < 30:
                return True
                
            await self._ensure_session()
            
            heartbeat_url = urljoin(self.server_url, '/api/v1/heartbeat')
            heartbeat_data = {
                'timestamp': current_time,
                'status': 'alive'
            }
            
            async with self._session.post(heartbeat_url, json=heartbeat_data) as response:
                if response.status == 200:
                    self._last_heartbeat = current_time
                    self.logger.debug("Heartbeat sent successfully")
                    return True
                else:
                    self.logger.warning(f"Heartbeat failed: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.debug(f"Heartbeat error: {e}")
            return False
    
    async def get_machine_config(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """Get machine-specific configuration from server"""
        try:
            await self._ensure_session()
            
            config_url = urljoin(self.server_url, f'/api/v1/machines/{machine_id}/config')
            
            async with self._session.get(config_url) as response:
                if response.status == 200:
                    config = await response.json()
                    self.logger.debug(f"Retrieved config for machine {machine_id}")
                    return config
                elif response.status == 404:
                    self.logger.debug(f"No specific config found for machine {machine_id}")
                    return None
                else:
                    self.logger.warning(f"Failed to get machine config: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting machine config: {e}")
            return None
    
    def get_server_url(self) -> str:
        """Get the server URL"""
        return self.server_url
    
    def is_connected(self) -> bool:
        """Check if connected to server"""
        return (self._session is not None and not self._session.closed) or \
               (self._websocket is not None and not self._websocket.closed)