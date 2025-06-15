# backend/app/services/hardware_simulator.py
import asyncio
import random
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
import uuid
import json

from app.core.config import settings
from app.models.machine import Machine as MachineModel, MachineType, ConnectionStatus
from app.models.metrics import MetricData as MetricModel, MetricType
from app.models.hardware import HardwareComponent as HardwareModel, ComponentType, ComponentStatus
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

class HardwareSimulator:
    def __init__(self):
        self.is_running = False
        self.machines: Dict[str, Dict] = {}
        self.simulation_task = None
        self.machine_templates = [
            {
                "name": "Server-01",
                "type": MachineType.SERVER,
                "motherboard": "ASUS PRIME X570-PRO",
                "cpu": {"name": "AMD Ryzen 9 5950X", "cores": 16, "threads": 32, "base_freq": 3.4, "max_freq": 4.9},
                "gpu": [{"name": "NVIDIA RTX 4090", "vram": 24576, "manufacturer": "NVIDIA"}],
                "ram": {"total": 32768, "modules": 4, "speed": 3200},
                "storage": [{"name": "Samsung 980 PRO", "capacity": 1024000, "type": "NVMe"}]
            },
            {
                "name": "Workstation-01",
                "type": MachineType.WORKSTATION,
                "motherboard": "MSI MEG X570 GODLIKE",
                "cpu": {"name": "Intel i9-13900K", "cores": 24, "threads": 32, "base_freq": 3.0, "max_freq": 5.8},
                "gpu": [{"name": "NVIDIA RTX 4080", "vram": 16384, "manufacturer": "NVIDIA"}],
                "ram": {"total": 64768, "modules": 8, "speed": 3600},
                "storage": [{"name": "WD Black SN850X", "capacity": 2048000, "type": "NVMe"}]
            },
            {
                "name": "Gaming-Rig",
                "type": MachineType.DESKTOP,
                "motherboard": "Gigabyte Z690 AORUS MASTER",
                "cpu": {"name": "Intel i7-13700K", "cores": 16, "threads": 24, "base_freq": 3.4, "max_freq": 5.4},
                "gpu": [{"name": "AMD RX 7900 XTX", "vram": 24576, "manufacturer": "AMD"}],
                "ram": {"total": 32768, "modules": 4, "speed": 3200},
                "storage": [{"name": "Corsair MP600 PRO", "capacity": 1024000, "type": "NVMe"}]
            },
            {
                "name": "AI-Server",
                "type": MachineType.SERVER,
                "motherboard": "ASUS WS C621E SAGE",
                "cpu": {"name": "Intel Xeon W-3375", "cores": 38, "threads": 76, "base_freq": 2.5, "max_freq": 4.0},
                "gpu": [
                    {"name": "NVIDIA A100", "vram": 40960, "manufacturer": "NVIDIA"},
                    {"name": "NVIDIA A100", "vram": 40960, "manufacturer": "NVIDIA"}
                ],
                "ram": {"total": 128000, "modules": 16, "speed": 2933},
                "storage": [{"name": "Intel Optane P5800X", "capacity": 800000, "type": "NVMe"}]
            },
            {
                "name": "Dev-Laptop",
                "type": MachineType.LAPTOP,
                "motherboard": "Apple M2 Max",
                "cpu": {"name": "Apple M2 Max", "cores": 12, "threads": 12, "base_freq": 3.2, "max_freq": 3.7},
                "gpu": [{"name": "Apple M2 Max GPU", "vram": 32768, "manufacturer": "Apple"}],
                "ram": {"total": 32768, "modules": 1, "speed": 6400},
                "storage": [{"name": "Apple SSD", "capacity": 1024000, "type": "NVMe"}]
            },
            {
                "name": "ML-Workstation",
                "type": MachineType.WORKSTATION,
                "motherboard": "ASUS Pro WS X570-ACE",
                "cpu": {"name": "AMD Threadripper PRO 5975WX", "cores": 32, "threads": 64, "base_freq": 3.6, "max_freq": 4.5},
                "gpu": [
                    {"name": "NVIDIA RTX 4090", "vram": 24576, "manufacturer": "NVIDIA"},
                    {"name": "NVIDIA RTX 4090", "vram": 24576, "manufacturer": "NVIDIA"}
                ],
                "ram": {"total": 256000, "modules": 8, "speed": 3200},
                "storage": [{"name": "Samsung 980 PRO", "capacity": 2048000, "type": "NVMe"}]
            },
            {
                "name": "Edge-Device",
                "type": MachineType.EMBEDDED,
                "motherboard": "NVIDIA Jetson AGX Orin",
                "cpu": {"name": "ARM Cortex-A78AE", "cores": 12, "threads": 12, "base_freq": 2.2, "max_freq": 2.2},
                "gpu": [{"name": "NVIDIA Ampere GPU", "vram": 32768, "manufacturer": "NVIDIA"}],
                "ram": {"total": 32768, "modules": 1, "speed": 3200},
                "storage": [{"name": "SanDisk Industrial", "capacity": 256000, "type": "eMMC"}]
            },
            {
                "name": "Database-Server",
                "type": MachineType.SERVER,
                "motherboard": "Supermicro X12SPG-TF",
                "cpu": {"name": "Intel Xeon Gold 6348", "cores": 28, "threads": 56, "base_freq": 2.6, "max_freq": 3.5},
                "gpu": [{"name": "NVIDIA T1000", "vram": 4096, "manufacturer": "NVIDIA"}],
                "ram": {"total": 512000, "modules": 16, "speed": 3200},
                "storage": [
                    {"name": "Intel DC P4610", "capacity": 1600000, "type": "NVMe"},
                    {"name": "Intel DC P4610", "capacity": 1600000, "type": "NVMe"}
                ]
            }
        ]
    
    async def start(self):
        """Start the hardware simulator"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting hardware simulator...")
        
        # Initialize simulated machines
        await self._initialize_machines()
        
        # Start simulation loop
        self.simulation_task = asyncio.create_task(self._simulation_loop())
        
        logger.info(f"Hardware simulator started with {len(self.machines)} machines")
    
    async def stop(self):
        """Stop the hardware simulator"""
        self.is_running = False
        
        if self.simulation_task:
            self.simulation_task.cancel()
            try:
                await self.simulation_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Hardware simulator stopped")
    
    async def _initialize_machines(self):
        """Initialize simulated machines in database"""
        db = SessionLocal()
        try:
            # Create machines from templates
            for i, template in enumerate(self.machine_templates[:settings.SIMULATOR_MACHINE_COUNT]):
                machine_id = str(uuid.uuid4())
                
                # Create machine in database
                machine_data = {
                    "id": machine_id,
                    "name": template["name"],
                    "ip_address": f"192.168.1.{100 + i}",
                    "port": 8001,
                    "machine_type": template["type"],
                    "status": ConnectionStatus.ONLINE,
                    "hostname": template["name"].lower().replace("-", ""),
                    "os_name": "Ubuntu" if template["type"] == MachineType.SERVER else "Windows",
                    "os_version": "22.04 LTS" if template["type"] == MachineType.SERVER else "11 Pro",
                    "architecture": "x86_64",
                    "motherboard_model": template["motherboard"].lower().replace(" ", "_"),
                    "last_seen": datetime.utcnow(),
                    "hardware_info": {
                        "cpu": template["cpu"],
                        "gpu": template["gpu"],
                        "ram": template["ram"],
                        "storage": template["storage"]
                    }
                }
                
                # Check if machine already exists
                existing = db.query(MachineModel).filter(MachineModel.ip_address == machine_data["ip_address"]).first()
                if not existing:
                    db_machine = MachineModel(**machine_data)
                    db.add(db_machine)
                else:
                    # Update existing machine
                    for key, value in machine_data.items():
                        if key != "id":
                            setattr(existing, key, value)
                    machine_id = str(existing.id)
                
                # Store machine state for simulation
                self.machines[machine_id] = {
                    "template": template,
                    "state": {
                        "cpu_usage": random.uniform(10, 30),
                        "memory_usage": random.uniform(20, 40),
                        "gpu_usage": random.uniform(0, 20),
                        "temperatures": {
                            "cpu": random.uniform(35, 45),
                            "gpu": random.uniform(30, 40),
                            "motherboard": random.uniform(25, 35)
                        },
                        "workload_pattern": random.choice(["idle", "normal", "burst", "sustained"]),
                        "last_pattern_change": datetime.utcnow()
                    }
                }
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error initializing simulated machines: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _simulation_loop(self):
        """Main simulation loop"""
        while self.is_running:
            try:
                await self._update_machine_states()
                await self._generate_metrics()
                await asyncio.sleep(settings.SIMULATOR_UPDATE_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
                await asyncio.sleep(5)
    
    async def _update_machine_states(self):
        """Update machine states with realistic patterns"""
        current_time = datetime.utcnow()
        
        for machine_id, machine_data in self.machines.items():
            state = machine_data["state"]
            template = machine_data["template"]
            
            # Change workload patterns periodically
            if (current_time - state["last_pattern_change"]).seconds > random.randint(300, 1800):
                state["workload_pattern"] = random.choice(["idle", "normal", "burst", "sustained"])
                state["last_pattern_change"] = current_time
            
            # Update CPU usage based on workload pattern
            pattern = state["workload_pattern"]
            if pattern == "idle":
                target_cpu = random.uniform(5, 15)
            elif pattern == "normal":
                target_cpu = random.uniform(20, 40)
            elif pattern == "burst":
                target_cpu = random.uniform(70, 95)
            else:  # sustained
                target_cpu = random.uniform(50, 70)
            
            # Smooth transitions
            state["cpu_usage"] += (target_cpu - state["cpu_usage"]) * 0.1
            state["cpu_usage"] = max(0, min(100, state["cpu_usage"]))
            
            # Memory usage correlates with CPU usage
            target_memory = state["cpu_usage"] * 0.8 + random.uniform(10, 20)
            state["memory_usage"] += (target_memory - state["memory_usage"]) * 0.05
            state["memory_usage"] = max(10, min(95, state["memory_usage"]))
            
            # GPU usage for machines with GPUs
            if template["gpu"]:
                if "AI" in template["name"] or "ML" in template["name"]:
                    target_gpu = random.uniform(60, 90) if pattern in ["burst", "sustained"] else random.uniform(10, 30)
                else:
                    target_gpu = random.uniform(0, 20)
                
                state["gpu_usage"] += (target_gpu - state.get("gpu_usage", 0)) * 0.1
                state["gpu_usage"] = max(0, min(100, state.get("gpu_usage", 0)))
            
            # Temperature based on usage
            base_temp = 25 + (state["cpu_usage"] * 0.5)
            state["temperatures"]["cpu"] = base_temp + random.uniform(-2, 5)
            
            if template["gpu"]:
                gpu_temp = 30 + (state.get("gpu_usage", 0) * 0.4)
                state["temperatures"]["gpu"] = gpu_temp + random.uniform(-3, 7)
            
            state["temperatures"]["motherboard"] = base_temp * 0.7 + random.uniform(-2, 3)
    
    async def _generate_metrics(self):
        """Generate realistic metrics for all machines"""
        db = SessionLocal()
        try:
            current_time = datetime.utcnow()
            metrics_batch = []
            
            for machine_id, machine_data in self.machines.items():
                state = machine_data["state"]
                template = machine_data["template"]
                
                # CPU metrics
                metrics_batch.extend([
                    MetricModel(
                        machine_id=machine_id,
                        metric_type=MetricType.CPU_USAGE,
                        component_name="CPU",
                        value=state["cpu_usage"],
                        unit="%",
                        timestamp=current_time
                    ),
                    MetricModel(
                        machine_id=machine_id,
                        metric_type=MetricType.CPU_TEMPERATURE,
                        component_name="CPU",
                        value=state["temperatures"]["cpu"],
                        unit="°C",
                        timestamp=current_time
                    ),
                    MetricModel(
                        machine_id=machine_id,
                        metric_type=MetricType.CPU_FREQUENCY,
                        component_name="CPU",
                        value=template["cpu"]["base_freq"] + (state["cpu_usage"] / 100) * (template["cpu"]["max_freq"] - template["cpu"]["base_freq"]),
                        unit="GHz",
                        timestamp=current_time
                    )
                ])
                
                # Memory metrics
                total_memory = template["ram"]["total"]
                used_memory = (state["memory_usage"] / 100) * total_memory
                metrics_batch.extend([
                    MetricModel(
                        machine_id=machine_id,
                        metric_type=MetricType.MEMORY_USAGE,
                        component_name="RAM",
                        value=state["memory_usage"],
                        unit="%",
                        timestamp=current_time
                    ),
                    MetricModel(
                        machine_id=machine_id,
                        metric_type=MetricType.MEMORY_AVAILABLE,
                        component_name="RAM",
                        value=total_memory - used_memory,
                        unit="MB",
                        timestamp=current_time
                    )
                ])
                
                # GPU metrics
                if template["gpu"]:
                    for i, gpu in enumerate(template["gpu"]):
                        gpu_usage = state.get("gpu_usage", 0) + random.uniform(-5, 5)
                        gpu_usage = max(0, min(100, gpu_usage))
                        
                        metrics_batch.extend([
                            MetricModel(
                                machine_id=machine_id,
                                metric_type=MetricType.GPU_USAGE,
                                component_name=f"GPU{i}",
                                value=gpu_usage,
                                unit="%",
                                timestamp=current_time
                            ),
                            MetricModel(
                                machine_id=machine_id,
                                metric_type=MetricType.GPU_MEMORY,
                                component_name=f"GPU{i}",
                                value=(gpu_usage / 100) * gpu["vram"],
                                unit="MB",
                                timestamp=current_time
                            ),
                            MetricModel(
                                machine_id=machine_id,
                                metric_type=MetricType.GPU_TEMPERATURE,
                                component_name=f"GPU{i}",
                                value=state["temperatures"].get("gpu", 40),
                                unit="°C",
                                timestamp=current_time
                            )
                        ])
                
                # Storage metrics
                for i, storage in enumerate(template["storage"]):
                    usage_percent = random.uniform(30, 80)
                    metrics_batch.extend([
                        MetricModel(
                            machine_id=machine_id,
                            metric_type=MetricType.DISK_USAGE,
                            component_name=f"Storage{i}",
                            value=usage_percent,
                            unit="%",
                            timestamp=current_time
                        ),
                        MetricModel(
                            machine_id=machine_id,
                            metric_type=MetricType.DISK_IO_READ,
                            component_name=f"Storage{i}",
                            value=random.uniform(10, 500),
                            unit="MB/s",
                            timestamp=current_time
                        ),
                        MetricModel(
                            machine_id=machine_id,
                            metric_type=MetricType.DISK_IO_WRITE,
                            component_name=f"Storage{i}",
                            value=random.uniform(5, 200),
                            unit="MB/s",
                            timestamp=current_time
                        )
                    ])
                
                # Network metrics
                metrics_batch.extend([
                    MetricModel(
                        machine_id=machine_id,
                        metric_type=MetricType.NETWORK_IO_SENT,
                        component_name="eth0",
                        value=random.uniform(1, 100),
                        unit="MB/s",
                        timestamp=current_time
                    ),
                    MetricModel(
                        machine_id=machine_id,
                        metric_type=MetricType.NETWORK_IO_RECV,
                        component_name="eth0",
                        value=random.uniform(1, 50),
                        unit="MB/s",
                        timestamp=current_time
                    )
                ])
                
                # System metrics
                metrics_batch.extend([
                    MetricModel(
                        machine_id=machine_id,
                        metric_type=MetricType.PROCESS_COUNT,
                        component_name="System",
                        value=random.randint(150, 400),
                        unit="count",
                        timestamp=current_time
                    ),
                    MetricModel(
                        machine_id=machine_id,
                        metric_type=MetricType.UPTIME,
                        component_name="System",
                        value=random.randint(100000, 1000000),
                        unit="seconds",
                        timestamp=current_time
                    ),
                    MetricModel(
                        machine_id=machine_id,
                        metric_type=MetricType.POWER_CONSUMPTION,
                        component_name="System",
                        value=100 + (state["cpu_usage"] * 2) + (state.get("gpu_usage", 0) * 3),
                        unit="W",
                        timestamp=current_time
                    )
                ])
            
            # Batch insert metrics
            db.add_all(metrics_batch)
            db.commit()
            
            logger.debug(f"Generated {len(metrics_batch)} metrics for {len(self.machines)} machines")
            
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_machine_count(self) -> int:
        """Get number of simulated machines"""
        return len(self.machines)
    
    def get_machine_states(self) -> Dict[str, Any]:
        """Get current states of all simulated machines"""
        return {mid: data["state"] for mid, data in self.machines.items()}