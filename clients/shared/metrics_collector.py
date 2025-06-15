#!/usr/bin/env python3
"""
System Metrics Collector
Cross-platform system metrics collection module for Master Dashboard agents
"""

import asyncio
import logging
import platform
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

import psutil

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# Platform-specific imports
if platform.system() == "Windows":
    try:
        import wmi
        WMI_AVAILABLE = True
    except ImportError:
        WMI_AVAILABLE = False
else:
    WMI_AVAILABLE = False

class SystemMetricsCollector:
    """Collects comprehensive system metrics across different platforms"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()
        
        # Initialize platform-specific components
        if self.platform == "windows" and WMI_AVAILABLE:
            try:
                self.wmi_conn = wmi.WMI()
            except Exception as e:
                self.logger.warning(f"Failed to initialize WMI: {e}")
                self.wmi_conn = None
        else:
            self.wmi_conn = None
            
        # Cache for metrics that don't change frequently
        self._static_info_cache = None
        self._network_interface_cache = None
        self._disk_info_cache = None
        
    async def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        try:
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'platform': self.platform,
                'uptime': self._get_system_uptime()
            }
            
            # Collect different metric categories
            if self._is_metric_enabled('cpu'):
                metrics['cpu'] = await self.collect_cpu_metrics()
                
            if self._is_metric_enabled('memory'):
                metrics['memory'] = await self.collect_memory_metrics()
                
            if self._is_metric_enabled('disk'):
                metrics['disk'] = await self.collect_disk_metrics()
                
            if self._is_metric_enabled('network'):
                metrics['network'] = await self.collect_network_metrics()
                
            if self._is_metric_enabled('gpu') and GPU_AVAILABLE:
                metrics['gpu'] = await self.collect_gpu_metrics()
                
            # Add system load information
            metrics['system'] = await self.collect_system_metrics()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'platform': self.platform
            }
    
    async def collect_cpu_metrics(self) -> Dict[str, Any]:
        """Collect CPU-related metrics"""
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True) if self._get_config('cpu.collect_per_core', True) else []
            
            cpu_metrics = {
                'usage_percent': cpu_percent,
                'core_count_logical': psutil.cpu_count(logical=True),
                'core_count_physical': psutil.cpu_count(logical=False),
                'frequency': self._get_cpu_frequency(),
                'load_average': self._get_load_average(),
                'per_core_usage': cpu_per_core
            }
            
            # Add CPU temperature if available
            if self._get_config('cpu.collect_temperature', False):
                cpu_metrics['temperature'] = await self._get_cpu_temperature()
                
            return cpu_metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting CPU metrics: {e}")
            return {'error': str(e)}
    
    async def collect_memory_metrics(self) -> Dict[str, Any]:
        """Collect memory-related metrics"""
        try:
            # Virtual memory
            virtual_mem = psutil.virtual_memory()
            
            memory_metrics = {
                'total': virtual_mem.total,
                'available': virtual_mem.available,
                'used': virtual_mem.used,
                'usage_percent': virtual_mem.percent,
                'free': virtual_mem.free
            }
            
            # Add platform-specific memory info
            if hasattr(virtual_mem, 'active'):
                memory_metrics['active'] = virtual_mem.active
            if hasattr(virtual_mem, 'inactive'):
                memory_metrics['inactive'] = virtual_mem.inactive
            if hasattr(virtual_mem, 'buffers'):
                memory_metrics['buffers'] = virtual_mem.buffers
            if hasattr(virtual_mem, 'cached'):
                memory_metrics['cached'] = virtual_mem.cached
                
            # Swap memory
            if self._get_config('memory.collect_swap', True):
                swap_mem = psutil.swap_memory()
                memory_metrics['swap'] = {
                    'total': swap_mem.total,
                    'used': swap_mem.used,
                    'free': swap_mem.free,
                    'usage_percent': swap_mem.percent
                }
                
            return memory_metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting memory metrics: {e}")
            return {'error': str(e)}
    
    async def collect_disk_metrics(self) -> Dict[str, Any]:
        """Collect disk-related metrics"""
        try:
            disk_metrics = {
                'partitions': [],
                'io': {}
            }
            
            # Disk partitions and usage
            partitions = psutil.disk_partitions()
            excluded_fs = self._get_config('disk.exclude_filesystems', [])
            
            for partition in partitions:
                if partition.fstype in excluded_fs:
                    continue
                    
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partition_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'usage_percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
                    }
                    disk_metrics['partitions'].append(partition_info)
                except (PermissionError, OSError) as e:
                    self.logger.debug(f"Could not access partition {partition.device}: {e}")
                    continue
            
            # Disk I/O statistics
            if self._get_config('disk.collect_io', True):
                try:
                    disk_io = psutil.disk_io_counters()
                    if disk_io:
                        disk_metrics['io'] = {
                            'read_count': disk_io.read_count,
                            'write_count': disk_io.write_count,
                            'read_bytes': disk_io.read_bytes,
                            'write_bytes': disk_io.write_bytes,
                            'read_time': disk_io.read_time,
                            'write_time': disk_io.write_time
                        }
                except Exception as e:
                    self.logger.debug(f"Could not collect disk I/O: {e}")
                    
            return disk_metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting disk metrics: {e}")
            return {'error': str(e)}
    
    async def collect_network_metrics(self) -> Dict[str, Any]:
        """Collect network-related metrics"""
        try:
            network_metrics = {
                'interfaces': {},
                'connections': 0,
                'io': {}
            }
            
            excluded_interfaces = self._get_config('network.exclude_interfaces', [])
            
            # Network interfaces
            network_stats = psutil.net_io_counters(pernic=True)
            for interface, stats in network_stats.items():
                if interface in excluded_interfaces:
                    continue
                    
                network_metrics['interfaces'][interface] = {
                    'bytes_sent': stats.bytes_sent,
                    'bytes_recv': stats.bytes_recv,
                    'packets_sent': stats.packets_sent,
                    'packets_recv': stats.packets_recv,
                    'errors_in': stats.errin,
                    'errors_out': stats.errout,
                    'drops_in': stats.dropin,
                    'drops_out': stats.dropout
                }
            
            # Total network I/O
            total_io = psutil.net_io_counters()
            if total_io:
                network_metrics['io'] = {
                    'bytes_sent': total_io.bytes_sent,
                    'bytes_recv': total_io.bytes_recv,
                    'packets_sent': total_io.packets_sent,
                    'packets_recv': total_io.packets_recv
                }
            
            # Network connections count
            try:
                connections = psutil.net_connections()
                network_metrics['connections'] = len(connections)
                
                # Connection states
                states = {}
                for conn in connections:
                    state = conn.status
                    states[state] = states.get(state, 0) + 1
                network_metrics['connection_states'] = states
                
            except (PermissionError, psutil.AccessDenied):
                self.logger.debug("Insufficient permissions to collect network connections")
                
            return network_metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting network metrics: {e}")
            return {'error': str(e)}
    
    async def collect_gpu_metrics(self) -> Dict[str, Any]:
        """Collect GPU-related metrics"""
        try:
            if not GPU_AVAILABLE:
                return {'error': 'GPU monitoring not available'}
                
            gpu_metrics = {
                'devices': []
            }
            
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                gpu_info = {
                    'id': gpu.id,
                    'name': gpu.name,
                    'uuid': gpu.uuid,
                    'temperature': gpu.temperature,
                    'utilization': gpu.load * 100,  # Convert to percentage
                    'memory_total': gpu.memoryTotal,
                    'memory_used': gpu.memoryUsed,
                    'memory_free': gpu.memoryFree,
                    'memory_usage_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100 if gpu.memoryTotal > 0 else 0
                }
                gpu_metrics['devices'].append(gpu_info)
                
            return gpu_metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting GPU metrics: {e}")
            return {'error': str(e)}
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect general system metrics"""
        try:
            system_metrics = {
                'boot_time': psutil.boot_time(),
                'process_count': len(psutil.pids()),
            }
            
            # System load (Unix-like systems)
            if hasattr(psutil, 'getloadavg'):
                try:
                    load_avg = psutil.getloadavg()
                    system_metrics['load_average'] = {
                        '1min': load_avg[0],
                        '5min': load_avg[1],
                        '15min': load_avg[2]
                    }
                except OSError:
                    pass
            
            # Top processes by CPU usage
            try:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Sort by CPU usage and get top 5
                top_processes = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:5]
                system_metrics['top_processes'] = top_processes
                
            except Exception as e:
                self.logger.debug(f"Could not collect process information: {e}")
                
            return system_metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {'error': str(e)}
    
    def _get_cpu_frequency(self) -> Dict[str, float]:
        """Get CPU frequency information"""
        try:
            freq = psutil.cpu_freq()
            if freq:
                return {
                    'current': freq.current,
                    'min': freq.min,
                    'max': freq.max
                }
        except Exception:
            pass
        return {}
    
    def _get_load_average(self) -> Optional[List[float]]:
        """Get system load average (Unix-like systems only)"""
        try:
            if hasattr(psutil, 'getloadavg'):
                return list(psutil.getloadavg())
        except Exception:
            pass
        return None
    
    async def _get_cpu_temperature(self) -> Optional[Dict[str, Any]]:
        """Get CPU temperature (platform-dependent)"""
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    cpu_temps = temps.get('cpu_thermal') or temps.get('coretemp') or temps.get('k8temp')
                    if cpu_temps:
                        return {
                            'current': cpu_temps[0].current,
                            'high': cpu_temps[0].high,
                            'critical': cpu_temps[0].critical
                        }
        except Exception as e:
            self.logger.debug(f"Could not collect CPU temperature: {e}")
        return None
    
    def _get_system_uptime(self) -> float:
        """Get system uptime in seconds"""
        try:
            return time.time() - psutil.boot_time()
        except Exception:
            return 0.0
    
    def _is_metric_enabled(self, metric_name: str) -> bool:
        """Check if a specific metric collection is enabled"""
        return self._get_config(f'metrics.{metric_name}.enabled', True)
    
    def _get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default