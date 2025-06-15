"""
System metrics collector for Master Dashboard Agent
Collects CPU, memory, disk, and system information with cross-platform support
"""
import asyncio
import platform
import psutil
import time
from typing import Dict, Any, List
import logging
from pathlib import Path
import json

class SystemMetricsCollector:
    """Collects comprehensive system metrics"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.system = platform.system().lower()
        self.boot_time = psutil.boot_time()
        self._cpu_count = psutil.cpu_count()
        self._cpu_count_logical = psutil.cpu_count(logical=True)
        
    async def collect(self) -> Dict[str, Any]:
        """Collect all system metrics"""
        try:
            metrics = {
                'timestamp': time.time(),
                'cpu': await self._collect_cpu_metrics(),
                'memory': await self._collect_memory_metrics(),
                'disk': await self._collect_disk_metrics(),
                'system': await self._collect_system_info(),
                'uptime': time.time() - self.boot_time
            }
            return metrics
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {'error': str(e)}
    
    async def _collect_cpu_metrics(self) -> Dict[str, Any]:
        """Collect CPU metrics"""
        # Get CPU usage over 1 second interval for accuracy
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        
        # CPU frequency
        cpu_freq = psutil.cpu_freq()
        freq_info = {
            'current': cpu_freq.current if cpu_freq else 0,
            'min': cpu_freq.min if cpu_freq else 0,
            'max': cpu_freq.max if cpu_freq else 0
        }
        
        # Load average (Unix systems only)
        load_avg = None
        try:
            if hasattr(psutil, 'getloadavg'):
                load_avg = psutil.getloadavg()
        except (AttributeError, OSError):
            pass
        
        # CPU stats
        cpu_stats = psutil.cpu_stats()
        
        return {
            'usage_percent': cpu_percent,
            'usage_per_core': cpu_per_core,
            'frequency': freq_info,
            'load_average': load_avg,
            'core_count_physical': self._cpu_count,
            'core_count_logical': self._cpu_count_logical,
            'stats': {
                'ctx_switches': cpu_stats.ctx_switches,
                'interrupts': cpu_stats.interrupts,
                'soft_interrupts': cpu_stats.soft_interrupts,
                'syscalls': getattr(cpu_stats, 'syscalls', 0)
            }
        }
    
    async def _collect_memory_metrics(self) -> Dict[str, Any]:
        """Collect memory metrics"""
        # Virtual memory
        virtual_mem = psutil.virtual_memory()
        
        # Swap memory
        swap_mem = psutil.swap_memory()
        
        return {
            'virtual': {
                'total': virtual_mem.total,
                'available': virtual_mem.available,
                'used': virtual_mem.used,
                'free': virtual_mem.free,
                'percent': virtual_mem.percent,
                'cached': getattr(virtual_mem, 'cached', 0),
                'buffers': getattr(virtual_mem, 'buffers', 0),
                'shared': getattr(virtual_mem, 'shared', 0)
            },
            'swap': {
                'total': swap_mem.total,
                'used': swap_mem.used,
                'free': swap_mem.free,
                'percent': swap_mem.percent,
                'sin': swap_mem.sin,
                'sout': swap_mem.sout
            }
        }
    
    async def _collect_disk_metrics(self) -> Dict[str, Any]:
        """Collect disk metrics"""
        disk_usage = {}
        disk_io = {}
        
        # Disk usage for each partition
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.device] = {
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
                }
            except (PermissionError, OSError) as e:
                self.logger.debug(f"Cannot access disk {partition.device}: {e}")
        
        # Disk I/O statistics
        try:
            disk_io_counters = psutil.disk_io_counters(perdisk=True)
            if disk_io_counters:
                for device, io_stats in disk_io_counters.items():
                    disk_io[device] = {
                        'read_count': io_stats.read_count,
                        'write_count': io_stats.write_count,
                        'read_bytes': io_stats.read_bytes,
                        'write_bytes': io_stats.write_bytes,
                        'read_time': io_stats.read_time,
                        'write_time': io_stats.write_time
                    }
        except Exception as e:
            self.logger.debug(f"Cannot get disk I/O stats: {e}")
        
        return {
            'usage': disk_usage,
            'io': disk_io
        }
    
    async def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information"""
        uname = platform.uname()
        
        # Boot time
        boot_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.boot_time))
        
        # User sessions
        users = []
        try:
            for user in psutil.users():
                users.append({
                    'name': user.name,
                    'terminal': user.terminal,
                    'host': user.host,
                    'started': user.started
                })
        except Exception as e:
            self.logger.debug(f"Cannot get user sessions: {e}")
        
        return {
            'hostname': uname.node,
            'system': uname.system,
            'release': uname.release,
            'version': uname.version,
            'machine': uname.machine,
            'processor': uname.processor,
            'architecture': platform.architecture(),
            'platform': platform.platform(),
            'boot_time': boot_time,
            'users': users,
            'python_version': platform.python_version()
        }