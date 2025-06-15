"""
Process monitor for Master Dashboard Agent
Tracks system processes with detailed resource consumption including CPU, memory, GPU, disk I/O, and network usage
"""
import asyncio
import psutil
import time
import logging
from typing import Dict, Any, List, Optional
import platform
import subprocess
import json

try:
    import pynvml
    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False

class ProcessMonitor:
    """Monitors system processes with detailed resource tracking"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.system = platform.system().lower()
        self.nvidia_initialized = False
        self._previous_stats = {}
        self._last_collection_time = 0
        
        # Initialize NVIDIA if available
        if NVIDIA_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.nvidia_initialized = True
            except Exception as e:
                self.logger.debug(f"NVIDIA ML not available: {e}")
    
    async def collect(self) -> Dict[str, Any]:
        """Collect comprehensive process information"""
        try:
            current_time = time.time()
            
            processes_data = {
                'timestamp': current_time,
                'processes': await self._collect_process_list(),
                'top_cpu': await self._get_top_processes_by_cpu(),
                'top_memory': await self._get_top_processes_by_memory(),
                'top_disk_io': await self._get_top_processes_by_disk_io(),
                'top_network': await self._get_top_processes_by_network(),
                'summary': await self._get_process_summary()
            }
            
            # Add GPU processes if available
            if self.nvidia_initialized:
                processes_data['top_gpu'] = await self._get_top_processes_by_gpu()
            
            # Calculate rates if we have previous data
            if self._previous_stats and self._last_collection_time:
                time_delta = current_time - self._last_collection_time
                processes_data['rates'] = self._calculate_process_rates(processes_data, time_delta)
            
            self._previous_stats = processes_data.copy()
            self._last_collection_time = current_time
            
            return processes_data
            
        except Exception as e:
            self.logger.error(f"Error collecting process data: {e}")
            return {'error': str(e)}
    
    async def _collect_process_list(self) -> List[Dict[str, Any]]:
        """Collect detailed information for all processes"""
        processes = []
        
        try:
            for proc in psutil.process_iter([
                'pid', 'name', 'username', 'status', 'create_time',
                'cpu_percent', 'memory_percent', 'memory_info',
                'cmdline', 'exe', 'cwd', 'num_threads', 'num_fds'
            ]):
                try:
                    proc_info = proc.info.copy()
                    
                    # Add additional information
                    proc_info['runtime'] = time.time() - proc_info['create_time']
                    proc_info['memory_rss'] = proc_info['memory_info'].rss if proc_info['memory_info'] else 0
                    proc_info['memory_vms'] = proc_info['memory_info'].vms if proc_info['memory_info'] else 0
                    
                    # Get I/O information
                    try:
                        io_counters = proc.io_counters()
                        proc_info['io'] = {
                            'read_count': io_counters.read_count,
                            'write_count': io_counters.write_count,
                            'read_bytes': io_counters.read_bytes,
                            'write_bytes': io_counters.write_bytes
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_info['io'] = None
                    
                    # Get network connections for this process
                    try:
                        connections = proc.connections()
                        proc_info['connections'] = len(connections)
                        proc_info['network_connections'] = [
                            {
                                'family': str(conn.family),
                                'type': str(conn.type),
                                'local': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                                'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                                'status': conn.status
                            } for conn in connections[:5]  # Limit to first 5 connections
                        ]
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_info['connections'] = 0
                        proc_info['network_connections'] = []
                    
                    # Get open files count
                    try:
                        open_files = proc.open_files()
                        proc_info['open_files'] = len(open_files)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_info['open_files'] = 0
                    
                    # Get parent process info
                    try:
                        parent = proc.parent()
                        if parent:
                            proc_info['parent_pid'] = parent.pid
                            proc_info['parent_name'] = parent.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_info['parent_pid'] = None
                        proc_info['parent_name'] = None
                    
                    # Get child processes
                    try:
                        children = proc.children()
                        proc_info['children_count'] = len(children)
                        proc_info['children_pids'] = [child.pid for child in children[:10]]  # Limit to first 10
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_info['children_count'] = 0
                        proc_info['children_pids'] = []
                    
                    processes.append(proc_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error collecting process list: {e}")
        
        return processes
    
    async def _get_top_processes_by_cpu(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top processes by CPU usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'username']):
                try:
                    cpu_percent = proc.cpu_percent()
                    if cpu_percent > 0:
                        processes.append({
                            'pid': proc.pid,
                            'name': proc.name(),
                            'cpu_percent': cpu_percent,
                            'username': proc.username()
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
        except Exception as e:
            self.logger.debug(f"Error getting top CPU processes: {e}")
            return []
    
    async def _get_top_processes_by_memory(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top processes by memory usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info', 'username']):
                try:
                    memory_info = proc.memory_info()
                    processes.append({
                        'pid': proc.pid,
                        'name': proc.name(),
                        'memory_percent': proc.memory_percent(),
                        'memory_rss': memory_info.rss,
                        'memory_vms': memory_info.vms,
                        'username': proc.username()
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:limit]
        except Exception as e:
            self.logger.debug(f"Error getting top memory processes: {e}")
            return []
    
    async def _get_top_processes_by_disk_io(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top processes by disk I/O"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    io_counters = proc.io_counters()
                    total_io = io_counters.read_bytes + io_counters.write_bytes
                    if total_io > 0:
                        processes.append({
                            'pid': proc.pid,
                            'name': proc.name(),
                            'read_bytes': io_counters.read_bytes,
                            'write_bytes': io_counters.write_bytes,
                            'total_io': total_io,
                            'username': proc.username()
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return sorted(processes, key=lambda x: x['total_io'], reverse=True)[:limit]
        except Exception as e:
            self.logger.debug(f"Error getting top disk I/O processes: {e}")
            return []
    
    async def _get_top_processes_by_network(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top processes by network connections"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    connections = proc.connections()
                    if connections:
                        processes.append({
                            'pid': proc.pid,
                            'name': proc.name(),
                            'connections_count': len(connections),
                            'username': proc.username(),
                            'connections': [
                                {
                                    'local': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                                    'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                                    'status': conn.status
                                } for conn in connections[:3]  # Show first 3 connections
                            ]
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return sorted(processes, key=lambda x: x['connections_count'], reverse=True)[:limit]
        except Exception as e:
            self.logger.debug(f"Error getting top network processes: {e}")
            return []
    
    async def _get_top_processes_by_gpu(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top processes by GPU usage (NVIDIA only)"""
        try:
            gpu_processes = []
            
            if not self.nvidia_initialized:
                return gpu_processes
            
            device_count = pynvml.nvmlDeviceGetCount()
            
            for gpu_id in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
                
                try:
                    processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
                    
                    for proc in processes:
                        try:
                            # Get process info from psutil
                            psutil_proc = psutil.Process(proc.pid)
                            
                            gpu_processes.append({
                                'pid': proc.pid,
                                'name': psutil_proc.name(),
                                'gpu_id': gpu_id,
                                'gpu_memory_used': proc.usedGpuMemory,
                                'username': psutil_proc.username()
                            })
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                            
                except pynvml.NVMLError:
                    continue
            
            return sorted(gpu_processes, key=lambda x: x['gpu_memory_used'], reverse=True)[:limit]
            
        except Exception as e:
            self.logger.debug(f"Error getting GPU processes: {e}")
            return []
    
    async def _get_process_summary(self) -> Dict[str, Any]:
        """Get summary statistics about processes"""
        try:
            total_processes = 0
            running_processes = 0
            sleeping_processes = 0
            zombie_processes = 0
            total_threads = 0
            
            for proc in psutil.process_iter(['status', 'num_threads']):
                try:
                    total_processes += 1
                    status = proc.status()
                    
                    if status == psutil.STATUS_RUNNING:
                        running_processes += 1
                    elif status == psutil.STATUS_SLEEPING:
                        sleeping_processes += 1
                    elif status == psutil.STATUS_ZOMBIE:
                        zombie_processes += 1
                    
                    total_threads += proc.num_threads()
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'total_processes': total_processes,
                'running_processes': running_processes,
                'sleeping_processes': sleeping_processes,
                'zombie_processes': zombie_processes,
                'total_threads': total_threads
            }
            
        except Exception as e:
            self.logger.debug(f"Error getting process summary: {e}")
            return {}
    
    def _calculate_process_rates(self, current_data: Dict, time_delta: float) -> Dict[str, Any]:
        """Calculate process resource usage rates"""
        rates = {}
        
        try:
            # Calculate I/O rates for top processes
            if 'top_disk_io' in current_data and 'top_disk_io' in self._previous_stats:
                rates['disk_io_rates'] = []
                
                for current_proc in current_data['top_disk_io']:
                    pid = current_proc['pid']
                    
                    # Find matching process in previous data
                    prev_proc = None
                    for p in self._previous_stats['top_disk_io']:
                        if p['pid'] == pid:
                            prev_proc = p
                            break
                    
                    if prev_proc:
                        read_rate = (current_proc['read_bytes'] - prev_proc['read_bytes']) / time_delta
                        write_rate = (current_proc['write_bytes'] - prev_proc['write_bytes']) / time_delta
                        
                        rates['disk_io_rates'].append({
                            'pid': pid,
                            'name': current_proc['name'],
                            'read_rate': max(0, read_rate),
                            'write_rate': max(0, write_rate)
                        })
                        
        except Exception as e:
            self.logger.debug(f"Error calculating process rates: {e}")
        
        return rates