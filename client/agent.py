#!/usr/bin/env python3
"""
Master Dashboard System Monitoring Agent
Collects system metrics and sends them to the Master Dashboard server
"""
import asyncio
import json
import platform
import sys
from pathlib import Path
from typing import Dict, Any
import yaml
import logging
from datetime import datetime, timezone

from collectors.system_metrics import SystemMetricsCollector
from collectors.hardware_sensors import HardwareSensorsCollector
from collectors.network_stats import NetworkStatsCollector
from communication.websocket_client import WebSocketClient
from communication.http_client import HTTPClient
from utils.logger import setup_logger
from utils.crypto import generate_machine_id

class MasterDashboardAgent:
    """Main agent class that orchestrates metric collection and transmission"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logger = setup_logger(
            name="master_dashboard_agent",
            level=self.config.get('logging', {}).get('level', 'INFO'),
            log_file=self.config.get('logging', {}).get('file', 'agent.log')
        )
        
        # Initialize collectors
        self.system_collector = SystemMetricsCollector(self.logger)
        self.hardware_collector = HardwareSensorsCollector(self.logger)
        self.network_collector = NetworkStatsCollector(self.logger)
        
        # Initialize communication clients
        self.ws_client = None
        self.http_client = HTTPClient(
            base_url=self.config['server']['url'],
            api_key=self.config['authentication']['api_key'],
            logger=self.logger
        )
        
        # Machine identification
        self.machine_id = generate_machine_id()
        self.machine_info = self._get_machine_info()
        
        self.running = False
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            # Create default config
            default_config = {
                'server': {
                    'url': 'http://localhost:8000',
                    'websocket_url': 'ws://localhost:8000/ws',
                    'reconnect_interval': 5
                },
                'authentication': {
                    'api_key': 'your-api-key-here'
                },
                'collection': {
                    'interval': 5,
                    'metrics': {
                        'system': True,
                        'hardware': True,
                        'network': True
                    }
                },
                'logging': {
                    'level': 'INFO',
                    'file': 'agent.log'
                }
            }
            
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            
            return default_config
    
    def _get_machine_info(self) -> Dict[str, Any]:
        """Get basic machine information"""
        return {
            'machine_id': self.machine_id,
            'hostname': platform.node(),
            'platform': platform.platform(),
            'system': platform.system(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    async def start(self):
        """Start the monitoring agent"""
        self.logger.info(f"Starting Master Dashboard Agent on {self.machine_info['hostname']}")
        self.logger.info(f"Machine ID: {self.machine_id}")
        
        # Register machine with server
        await self._register_machine()
        
        # Initialize WebSocket connection
        if self.config['server'].get('websocket_url'):
            self.ws_client = WebSocketClient(
                url=self.config['server']['websocket_url'],
                machine_id=self.machine_id,
                api_key=self.config['authentication']['api_key'],
                logger=self.logger
            )
            await self.ws_client.connect()
        
        self.running = True
        
        # Start main monitoring loop
        await self._monitoring_loop()
    
    async def stop(self):
        """Stop the monitoring agent"""
        self.logger.info("Stopping Master Dashboard Agent")
        self.running = False
        
        if self.ws_client:
            await self.ws_client.disconnect()
    
    async def _register_machine(self):
        """Register this machine with the server"""
        try:
            response = await self.http_client.post('/api/v1/machines/register', {
                'machine_info': self.machine_info,
                'agent_version': '1.0.0',
                'capabilities': {
                    'system_metrics': True,
                    'hardware_sensors': True,
                    'network_stats': True
                }
            })
            
            if response.get('success'):
                self.logger.info("Machine registered successfully")
            else:
                self.logger.warning(f"Machine registration failed: {response.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Failed to register machine: {e}")
    
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect all enabled metrics"""
        metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'machine_id': self.machine_id
        }
        
        config_metrics = self.config['collection']['metrics']
        
        try:
            if config_metrics.get('system', True):
                metrics['system'] = await self.system_collector.collect()
            
            if config_metrics.get('hardware', True):
                metrics['hardware'] = await self.hardware_collector.collect()
            
            if config_metrics.get('network', True):
                metrics['network'] = await self.network_collector.collect()
                
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            metrics['error'] = str(e)
        
        return metrics
    
    async def _send_metrics(self, metrics: Dict[str, Any]):
        """Send metrics to the server"""
        try:
            # Try WebSocket first if available
            if self.ws_client and self.ws_client.is_connected():
                await self.ws_client.send_metrics(metrics)
                return
            
            # Fallback to HTTP
            response = await self.http_client.post('/api/v1/metrics', metrics)
            if not response.get('success'):
                self.logger.warning(f"HTTP metrics send failed: {response.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Failed to send metrics: {e}")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        interval = self.config['collection']['interval']
        
        while self.running:
            try:
                # Collect metrics
                metrics = await self._collect_metrics()
                
                # Send metrics
                await self._send_metrics(metrics)
                
                # Log successful collection
                if 'error' not in metrics:
                    self.logger.debug(f"Metrics collected and sent successfully")
                
                # Wait for next collection
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)

async def main():
    """Main entry point"""
    config_path = "config.yaml"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    agent = MasterDashboardAgent(config_path)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await agent.stop()

if __name__ == "__main__":
    if platform.system() == "Windows":
        # Windows specific event loop policy
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())