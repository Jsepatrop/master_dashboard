#!/usr/bin/env python3
"""
Master Dashboard Data Simulator
Generates realistic machine metrics and sends them via WebSocket
"""

import asyncio
import websockets
import json
import random
import time
import logging
import math
from datetime import datetime
from typing import Dict, List, Any
import argparse
import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MachineSimulator:
    def __init__(self, machine_id: str, machine_type: str, machine_name: str):
        self.machine_id = machine_id
        self.machine_type = machine_type
        self.machine_name = machine_name
        
        # Initialize baseline metrics
        self.cpu_baseline = random.uniform(20, 40)
        self.memory_baseline = random.uniform(2, 6)
        self.disk_baseline = random.uniform(100, 300)
        self.network_baseline = random.uniform(50, 150)
        
        # Trend factors for realistic variation
        self.cpu_trend = 0
        self.memory_trend = 0
        self.disk_trend = 0
        self.network_trend = 0
        
        # Load patterns based on machine type
        self.load_patterns = self._get_load_patterns()
        
    def _get_load_patterns(self) -> Dict[str, Dict[str, float]]:
        """Get load patterns based on machine type"""
        patterns = {
            'WEB_SERVER': {
                'cpu_variance': 15,
                'memory_variance': 2,
                'disk_variance': 50,
                'network_variance': 100,
                'spike_probability': 0.1
            },
            'DATABASE_SERVER': {
                'cpu_variance': 20,
                'memory_variance': 4,
                'disk_variance': 100,
                'network_variance': 80,
                'spike_probability': 0.15
            },
            'APPLICATION_SERVER': {
                'cpu_variance': 18,
                'memory_variance': 3,
                'disk_variance': 75,
                'network_variance': 90,
                'spike_probability': 0.12
            },
            'LOAD_BALANCER': {
                'cpu_variance': 10,
                'memory_variance': 1,
                'disk_variance': 25,
                'network_variance': 200,
                'spike_probability': 0.08
            },
            'CACHE_SERVER': {
                'cpu_variance': 12,
                'memory_variance': 6,
                'disk_variance': 30,
                'network_variance': 120,
                'spike_probability': 0.1
            }
        }
        return patterns.get(self.machine_type, patterns['WEB_SERVER'])
    
    def generate_metrics(self) -> List[Dict[str, Any]]:
        """Generate realistic metrics for this machine"""
        current_time = datetime.now().isoformat()
        pattern = self.load_patterns
        
        # Generate some randomness and trends
        time_factor = time.time() / 3600  # Hour-based cycles
        
        # CPU Usage (0-100%)
        cpu_variation = random.uniform(-pattern['cpu_variance'], pattern['cpu_variance'])
        cpu_cycle = 10 * math.sin(time_factor * 2 * math.pi / 24)  # Daily cycle
        cpu_spike = 30 if random.random() < pattern['spike_probability'] else 0
        cpu_usage = max(0, min(100, self.cpu_baseline + cpu_variation + cpu_cycle + cpu_spike))
        
        # Memory Usage (0-16GB)
        memory_variation = random.uniform(-pattern['memory_variance'], pattern['memory_variance'])
        memory_cycle = 2 * math.sin(time_factor * 2 * math.pi / 12)  # 12-hour cycle
        memory_usage = max(0, min(16, self.memory_baseline + memory_variation + memory_cycle))
        
        # Disk Usage (0-1000GB)
        disk_variation = random.uniform(-pattern['disk_variance'], pattern['disk_variance'])
        disk_usage = max(0, min(1000, self.disk_baseline + disk_variation))
        
        # Network Throughput (0-1000Mbps)
        network_variation = random.uniform(-pattern['network_variance'], pattern['network_variance'])
        network_burst = 200 if random.random() < (pattern['spike_probability'] / 2) else 0
        network_usage = max(0, min(1000, self.network_baseline + network_variation + network_burst))
        
        # Create metric objects
        metrics = [
            {
                'id': f'metric-{int(time.time() * 1000)}-cpu-{self.machine_id}',
                'machine_id': self.machine_id,
                'metric_type': 'CPU_USAGE',
                'value': round(cpu_usage, 2),
                'unit': '%',
                'timestamp': current_time,
                'threshold_warning': 70.0,
                'threshold_critical': 90.0
            },
            {
                'id': f'metric-{int(time.time() * 1000)}-mem-{self.machine_id}',
                'machine_id': self.machine_id,
                'metric_type': 'MEMORY_USAGE',
                'value': round(memory_usage, 2),
                'unit': 'GB',
                'timestamp': current_time,
                'threshold_warning': 12.0,
                'threshold_critical': 14.0
            },
            {
                'id': f'metric-{int(time.time() * 1000)}-disk-{self.machine_id}',
                'machine_id': self.machine_id,
                'metric_type': 'DISK_USAGE',
                'value': round(disk_usage, 2),
                'unit': 'GB',
                'timestamp': current_time,
                'threshold_warning': 800.0,
                'threshold_critical': 950.0
            },
            {
                'id': f'metric-{int(time.time() * 1000)}-net-{self.machine_id}',
                'machine_id': self.machine_id,
                'metric_type': 'NETWORK_THROUGHPUT',
                'value': round(network_usage, 2),
                'unit': 'Mbps',
                'timestamp': current_time,
                'threshold_warning': 800.0,
                'threshold_critical': 950.0
            }
        ]
        
        return metrics

class DataSimulator:
    def __init__(self, backend_url: str, update_interval: int = 5):
        self.backend_url = backend_url
        self.update_interval = update_interval
        self.running = False
        self.websocket = None
        
        # Initialize machine simulators
        self.machines = [
            MachineSimulator('machine-001', 'WEB_SERVER', 'Web Server Alpha'),
            MachineSimulator('machine-002', 'DATABASE_SERVER', 'Database Cluster'),
            MachineSimulator('machine-003', 'LOAD_BALANCER', 'Load Balancer'),
            MachineSimulator('machine-004', 'CACHE_SERVER', 'Cache Server'),
            MachineSimulator('machine-005', 'APPLICATION_SERVER', 'App Server Beta')
        ]
        
        logger.info(f"Initialized {len(self.machines)} machine simulators")
    
    async def connect(self):
        """Connect to the backend WebSocket"""
        try:
            logger.info(f"Connecting to {self.backend_url}")
            self.websocket = await websockets.connect(self.backend_url)
            logger.info("Connected to Master Dashboard backend")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to backend: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the backend"""
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("Disconnected from backend")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
    
    async def send_metrics_batch(self, metrics_batch: List[Dict[str, Any]]):
        """Send a batch of metrics to the backend"""
        if not self.websocket:
            logger.error("WebSocket not connected")
            return False
        
        try:
            message = {
                'type': 'metrics_batch',
                'timestamp': datetime.now().isoformat(),
                'data': metrics_batch
            }
            
            await self.websocket.send(json.dumps(message))
            logger.debug(f"Sent {len(metrics_batch)} metrics to backend")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send metrics: {e}")
            return False
    
    async def simulation_loop(self):
        """Main simulation loop"""
        logger.info(f"Starting simulation loop (interval: {self.update_interval}s)")
        
        while self.running:
            try:
                # Generate metrics for all machines
                all_metrics = []
                for machine in self.machines:
                    machine_metrics = machine.generate_metrics()
                    all_metrics.extend(machine_metrics)
                
                # Send metrics batch
                success = await self.send_metrics_batch(all_metrics)
                
                if success:
                    logger.info(f"Generated and sent {len(all_metrics)} metrics for {len(self.machines)} machines")
                else:
                    logger.warning("Failed to send metrics batch")
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                logger.info("Simulation loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
                await asyncio.sleep(1)  # Brief pause before retry
    
    async def start(self):
        """Start the data simulator"""
        self.running = True
        
        # Connect with retry logic
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            if await self.connect():
                break
            
            if attempt < max_retries - 1:
                logger.warning(f"Connection attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("Max connection attempts reached, exiting")
                return
        
        # Start simulation loop
        try:
            await self.simulation_loop()
        finally:
            await self.disconnect()
    
    def stop(self):
        """Stop the data simulator"""
        logger.info("Stopping data simulator...")
        self.running = False



async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Master Dashboard Data Simulator')
    parser.add_argument(
        '--backend-url',
        default='ws://localhost:8000/ws/data',
        help='Backend WebSocket URL'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Update interval in seconds'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and start simulator
    simulator = DataSimulator(args.backend_url, args.interval)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        simulator.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await simulator.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        simulator.stop()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Simulator stopped by user")
        sys.exit(0)