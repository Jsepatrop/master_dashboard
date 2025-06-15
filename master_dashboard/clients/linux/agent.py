#!/usr/bin/env python3
"""
Master Dashboard Linux Agent
Collects system metrics and sends them to the Master Dashboard server
"""

import asyncio
import json
import logging
import os
import platform
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from metrics_collector import SystemMetricsCollector
from communication import DashboardCommunicator
from utils import setup_logging, load_config, create_machine_info

class LinuxAgent:
    def __init__(self, config_path: str = "config.json"):
        """Initialize the Linux agent"""
        self.config = load_config(config_path)
        self.logger = setup_logging(
            log_file=self.config.get('log_file', '/var/log/master-dashboard-agent.log'),
            log_level=self.config.get('log_level', 'INFO')
        )
        
        self.metrics_collector = SystemMetricsCollector()
        self.communicator = DashboardCommunicator(
            server_url=self.config['server']['url'],
            api_key=self.config['server'].get('api_key'),
            timeout=self.config['server'].get('timeout', 30)
        )
        
        self.machine_info = create_machine_info()
        self.running = True
        self.collection_interval = self.config.get('collection_interval', 5)
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    async def register_machine(self) -> bool:
        """Register this machine with the server"""
        try:
            self.logger.info("Registering machine with server...")
            success = await self.communicator.register_machine(self.machine_info)
            if success:
                self.logger.info("Machine registered successfully")
                return True
            else:
                self.logger.error("Failed to register machine")
                return False
        except Exception as e:
            self.logger.error(f"Error registering machine: {e}")
            return False
            
    async def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Send metrics to the server"""
        try:
            # Add machine identification to metrics
            metrics['machine_id'] = self.machine_info['id']
            metrics['hostname'] = self.machine_info['hostname']
            metrics['timestamp'] = datetime.utcnow().isoformat()
            
            success = await self.communicator.send_metrics(metrics)
            if not success:
                self.logger.warning("Failed to send metrics to server")
            return success
        except Exception as e:
            self.logger.error(f"Error sending metrics: {e}")
            return False
            
    async def run_collection_cycle(self):
        """Run one metrics collection cycle"""
        try:
            # Collect system metrics
            metrics = await self.metrics_collector.collect_all_metrics()
            
            # Send to server
            success = await self.send_metrics(metrics)
            
            if success:
                self.logger.debug("Metrics collected and sent successfully")
            else:
                self.logger.warning("Failed to send metrics")
                
        except Exception as e:
            self.logger.error(f"Error in collection cycle: {e}")
            
    async def run(self):
        """Main agent loop"""
        self.logger.info("Starting Master Dashboard Linux Agent")
        self.logger.info(f"Machine: {self.machine_info['hostname']} ({self.machine_info['os']})")
        self.logger.info(f"Server: {self.config['server']['url']}")
        self.logger.info(f"Collection interval: {self.collection_interval}s")
        
        # Register machine with server
        registration_success = await self.register_machine()
        if not registration_success:
            self.logger.error("Failed to register with server, continuing anyway...")
            
        # Start metrics collection loop
        while self.running:
            try:
                await self.run_collection_cycle()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
        self.logger.info("Agent stopped")
        
    async def test_connection(self) -> bool:
        """Test connection to the server"""
        try:
            self.logger.info("Testing connection to server...")
            success = await self.communicator.test_connection()
            if success:
                self.logger.info("✓ Connection test successful")
                return True
            else:
                self.logger.error("✗ Connection test failed")
                return False
        except Exception as e:
            self.logger.error(f"✗ Connection test error: {e}")
            return False

def main():
    """Main entry point"""
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Test mode - check connection and exit
            async def test():
                agent = LinuxAgent()
                success = await agent.test_connection()
                sys.exit(0 if success else 1)
            asyncio.run(test())
            return
        elif sys.argv[1] == "info":
            # Info mode - show machine info and exit
            machine_info = create_machine_info()
            print(json.dumps(machine_info, indent=2))
            return
            
    # Normal operation
    agent = LinuxAgent()
    
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()