"""
HTTP client for Master Dashboard Agent
Handles HTTP communication with the Master Dashboard server including authentication,
data transmission, and error handling with retry logic
"""
import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Any, Optional
import ssl
from urllib.parse import urljoin

class HTTPClient:
    """HTTP client for API communication with Master Dashboard server"""
    
    def __init__(self, base_url: str, api_key: str, logger: logging.Logger):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.logger = logger
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.max_retries = 3
        self.retry_delay = 1
        
        # SSL context for secure connections
        self.ssl_context = ssl.create_default_context()
        if base_url.startswith('https://'):
            self.ssl_context.check_hostname = True
            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                ssl=self.ssl_context,
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'MasterDashboard-Agent/1.0',
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
            )
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        return await self._request('GET', endpoint, params=params)
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request"""
        return await self._request('POST', endpoint, json=data)
    
    async def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request"""
        return await self._request('PUT', endpoint, json=data)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        return await self._request('DELETE', endpoint)
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        await self._ensure_session()
        
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.debug(f"{method} {url} (attempt {attempt + 1})")
                
                async with self.session.request(method, url, **kwargs) as response:
                    # Log response details
                    self.logger.debug(f"Response: {response.status} {response.reason}")
                    
                    # Read response text
                    response_text = await response.text()
                    
                    # Try to parse as JSON
                    try:
                        response_data = json.loads(response_text) if response_text else {}
                    except json.JSONDecodeError:
                        response_data = {'raw_response': response_text}
                    
                    # Handle different response codes
                    if response.status == 200:
                        return response_data
                    elif response.status == 201:
                        return response_data
                    elif response.status == 204:
                        return {'success': True, 'message': 'No content'}
                    elif response.status == 400:
                        error_msg = response_data.get('error', 'Bad request')
                        self.logger.error(f"Bad request: {error_msg}")
                        return {'success': False, 'error': error_msg}
                    elif response.status == 401:
                        error_msg = 'Authentication failed'
                        self.logger.error(error_msg)
                        return {'success': False, 'error': error_msg}
                    elif response.status == 403:
                        error_msg = 'Access forbidden'
                        self.logger.error(error_msg)
                        return {'success': False, 'error': error_msg}
                    elif response.status == 404:
                        error_msg = 'Endpoint not found'
                        self.logger.error(error_msg)
                        return {'success': False, 'error': error_msg}
                    elif response.status >= 500:
                        error_msg = f"Server error: {response.status}"
                        self.logger.error(error_msg)
                        if attempt < self.max_retries:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            continue
                        return {'success': False, 'error': error_msg}
                    else:
                        error_msg = f"Unexpected status: {response.status}"
                        self.logger.error(error_msg)
                        return {'success': False, 'error': error_msg}
                        
            except aiohttp.ClientError as e:
                error_msg = f"HTTP client error: {e}"
                self.logger.error(error_msg)
                
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
                return {'success': False, 'error': error_msg}
                
            except asyncio.TimeoutError:
                error_msg = "Request timeout"
                self.logger.error(error_msg)
                
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
                return {'success': False, 'error': error_msg}
                
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                self.logger.error(error_msg)
                
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
                return {'success': False, 'error': error_msg}
        
        return {'success': False, 'error': 'Max retries exceeded'}
    
    async def send_metrics_batch(self, metrics_list: list) -> Dict[str, Any]:
        """Send multiple metrics in a batch"""
        try:
            batch_data = {
                'timestamp': time.time(),
                'batch_size': len(metrics_list),
                'metrics': metrics_list
            }
            
            response = await self.post('/api/v1/metrics/batch', batch_data)
            
            if response.get('success', False):
                self.logger.debug(f"Sent batch of {len(metrics_list)} metrics")
            else:
                self.logger.warning(f"Batch send failed: {response.get('error', 'Unknown error')}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error sending metrics batch: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        try:
            response = await self.get('/api/v1/health')
            return response
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def register_machine(self, machine_info: Dict[str, Any]) -> Dict[str, Any]:
        """Register machine with server"""
        try:
            registration_data = {
                'machine_info': machine_info,
                'timestamp': time.time(),
                'agent_version': '1.0.0'
            }
            
            response = await self.post('/api/v1/machines/register', registration_data)
            
            if response.get('success', False):
                self.logger.info("Machine registered successfully")
            else:
                self.logger.warning(f"Machine registration failed: {response.get('error', 'Unknown error')}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error registering machine: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    async def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send alert to server"""
        try:
            alert_payload = {
                'timestamp': time.time(),
                'alert': alert_data
            }
            
            response = await self.post('/api/v1/alerts', alert_payload)
            
            if response.get('success', False):
                self.logger.info(f"Alert sent: {alert_data.get('level', 'unknown')} - {alert_data.get('message', 'no message')}")
            else:
                self.logger.warning(f"Alert send failed: {response.get('error', 'Unknown error')}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error sending alert: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}