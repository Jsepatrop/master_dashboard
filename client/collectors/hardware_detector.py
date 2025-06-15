"""
Hardware detector for Master Dashboard Agent
Automatically detects and identifies all available hardware components including
CPU, GPU, TPU, RAM, storage, network interfaces, and specialized accelerators
"""
import asyncio
import platform
import subprocess
import json
import logging
import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    import pynvml
    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False

try:
    import cpuinfo
    CPUINFO_AVAILABLE = True
except ImportError:
    CPUINFO_AVAILABLE = False

try:
    import distro
    DISTRO_AVAILABLE = True
except ImportError:
    DISTRO_AVAILABLE = False

class HardwareDetector:
    """Comprehensive hardware detection and identification system"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.system = platform.system().lower()
        self.machine_arch = platform.machine()
        self.detected_hardware = {}
        
    async def detect_all_hardware(self) -> Dict[str, Any]:
        """Detect all available hardware components"""
        try:
            hardware_info = {
                'timestamp': asyncio.get_event_loop().time(),
                'cpu': await self._detect_cpu(),
                'memory': await self._detect_memory(),
                'gpu': await self._detect_gpu(),
                'tpu': await self._detect_tpu(),
                'storage': await self._detect_storage(),
                'network': await self._detect_network_interfaces(),
                'motherboard': await self._detect_motherboard(),
                'accelerators': await self._detect_accelerators(),
                'sensors': await self._detect_available_sensors(),
                'capabilities': await self._detect_system_capabilities()
            }
            
            self.detected_hardware = hardware_info
            return hardware_info
            
        except Exception as e:
            self.logger.error(f"Error detecting hardware: {e}")
            return {'error': str(e)}
    
    async def _detect_cpu(self) -> Dict[str, Any]:
        """Detect CPU information"""
        cpu_info = {
            'cores_physical': os.cpu_count(),
            'cores_logical': os.cpu_count(),
            'architecture': platform.machine(),
            'byte_order': platform.architecture()[1],
            'features': []
        }
        
        try:
            if CPUINFO_AVAILABLE:
                info = cpuinfo.get_cpu_info()
                cpu_info.update({
                    'brand': info.get('brand_raw', 'Unknown'),
                    'vendor': info.get('vendor_id_raw', 'Unknown'),
                    'family': info.get('family', 0),
                    'model': info.get('model', 0),
                    'stepping': info.get('stepping', 0),
                    'flags': info.get('flags', []),
                    'hz_advertised': info.get('hz_advertised_friendly', 'Unknown'),
                    'hz_actual': info.get('hz_actual_friendly', 'Unknown'),
                    'l2_cache_size': info.get('l2_cache_size', 0),
                    'l3_cache_size': info.get('l3_cache_size', 0)
                })
            
            # Platform-specific CPU detection
            if self.system == 'linux':
                cpu_info.update(await self._detect_linux_cpu())
            elif self.system == 'windows':
                cpu_info.update(await self._detect_windows_cpu())
            elif self.system == 'darwin':
                cpu_info.update(await self._detect_macos_cpu())
                
        except Exception as e:
            self.logger.debug(f"Error detecting CPU details: {e}")
        
        return cpu_info
    
    async def _detect_linux_cpu(self) -> Dict[str, Any]:
        """Linux-specific CPU detection"""
        cpu_info = {}
        try:
            with open('/proc/cpuinfo', 'r') as f:
                content = f.read()
                
            # Parse CPU information
            cpu_info['model_name'] = re.search(r'model name\s*:\s*(.+)', content)
            if cpu_info['model_name']:
                cpu_info['model_name'] = cpu_info['model_name'].group(1).strip()
            
            # Get CPU frequency info
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'cpu MHz' in line:
                            cpu_info['current_freq_mhz'] = float(line.split(':')[1].strip())
                            break
            except:
                pass
                
        except Exception as e:
            self.logger.debug(f"Error reading Linux CPU info: {e}")
        
        return cpu_info
    
    async def _detect_windows_cpu(self) -> Dict[str, Any]:
        """Windows-specific CPU detection using WMI"""
        cpu_info = {}
        try:
            result = subprocess.run([
                'wmic', 'cpu', 'get', 'Name,Manufacturer,MaxClockSpeed,NumberOfCores,NumberOfLogicalProcessors', '/format:csv'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 6:
                            cpu_info.update({
                                'manufacturer': parts[1],
                                'max_clock_speed': parts[2],
                                'model_name': parts[3],
                                'cores_physical': parts[4],
                                'cores_logical': parts[5]
                            })
                            break
                            
        except Exception as e:
            self.logger.debug(f"Error detecting Windows CPU: {e}")
        
        return cpu_info
    
    async def _detect_macos_cpu(self) -> Dict[str, Any]:
        """macOS-specific CPU detection"""
        cpu_info = {}
        try:
            # Use system_profiler
            result = subprocess.run([
                'system_profiler', 'SPHardwareDataType', '-json'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                hardware_info = data.get('SPHardwareDataType', [{}])[0]
                
                cpu_info.update({
                    'model_name': hardware_info.get('cpu_type', 'Unknown'),
                    'cores_physical': hardware_info.get('number_processors', 0),
                    'l2_cache': hardware_info.get('l2_cache_core', 'Unknown'),
                    'l3_cache': hardware_info.get('l3_cache', 'Unknown')
                })
                
        except Exception as e:
            self.logger.debug(f"Error detecting macOS CPU: {e}")
        
        return cpu_info
    
    async def _detect_memory(self) -> Dict[str, Any]:
        """Detect memory configuration"""
        import psutil
        
        memory_info = {
            'total_ram': psutil.virtual_memory().total,
            'swap_total': psutil.swap_memory().total,
            'modules': []
        }
        
        try:
            if self.system == 'linux':
                # Try to get memory module information
                try:
                    result = subprocess.run(['dmidecode', '-t', 'memory'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        memory_info['modules'] = self._parse_dmidecode_memory(result.stdout)
                except:
                    pass
                    
            elif self.system == 'windows':
                try:
                    result = subprocess.run([
                        'wmic', 'memorychip', 'get', 'Capacity,Speed,Manufacturer,PartNumber', '/format:csv'
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        memory_info['modules'] = self._parse_wmic_memory(result.stdout)
                except:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Error detecting memory details: {e}")
        
        return memory_info
    
    async def _detect_gpu(self) -> Dict[str, Any]:
        """Detect GPU information"""
        gpu_info = {
            'nvidia': [],
            'amd': [],
            'intel': [],
            'other': []
        }
        
        # NVIDIA GPU detection
        if NVIDIA_AVAILABLE:
            try:
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle).decode()
                    
                    try:
                        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        driver_version = pynvml.nvmlSystemGetDriverVersion().decode()
                        cuda_version = pynvml.nvmlSystemGetCudaDriverVersion()
                        
                        gpu_data = {
                            'index': i,
                            'name': name,
                            'memory_total': memory_info.total,
                            'memory_free': memory_info.free,
                            'memory_used': memory_info.used,
                            'driver_version': driver_version,
                            'cuda_version': f"{cuda_version // 1000}.{(cuda_version % 1000) // 10}",
                            'compute_capability': self._get_compute_capability(handle),
                            'power_limit': self._get_power_limit(handle)
                        }
                        
                        gpu_info['nvidia'].append(gpu_data)
                        
                    except Exception as e:
                        self.logger.debug(f"Error getting NVIDIA GPU {i} details: {e}")
                        
            except Exception as e:
                self.logger.debug(f"NVIDIA GPU detection failed: {e}")
        
        # Platform-specific GPU detection for other vendors
        if self.system == 'linux':
            gpu_info.update(await self._detect_linux_gpu())
        elif self.system == 'windows':
            gpu_info.update(await self._detect_windows_gpu())
        elif self.system == 'darwin':
            gpu_info.update(await self._detect_macos_gpu())
        
        return gpu_info
    
    async def _detect_tpu(self) -> Dict[str, Any]:
        """Detect TPU and other AI accelerators"""
        tpu_info = {
            'google_tpu': [],
            'coral_tpu': [],
            'other_accelerators': []
        }
        
        try:
            # Check for Google Cloud TPU
            if os.path.exists('/dev/accel0') or os.path.exists('/sys/class/accel'):
                tpu_info['google_tpu'] = await self._detect_google_tpu()
            
            # Check for Coral TPU
            if self.system == 'linux':
                try:
                    result = subprocess.run(['lsusb'], capture_output=True, text=True)
                    if 'Google Inc.' in result.stdout and 'Coral' in result.stdout:
                        tpu_info['coral_tpu'] = await self._detect_coral_tpu()
                except:
                    pass
            
            # Check for other accelerators (Intel Movidius, etc.)
            tpu_info['other_accelerators'] = await self._detect_other_accelerators()
            
        except Exception as e:
            self.logger.debug(f"Error detecting TPU/accelerators: {e}")
        
        return tpu_info
    
    async def _detect_storage(self) -> Dict[str, Any]:
        """Detect storage devices"""
        import psutil
        
        storage_info = {
            'disks': [],
            'partitions': []
        }
        
        try:
            # Get disk information
            disk_partitions = psutil.disk_partitions()
            for partition in disk_partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    storage_info['partitions'].append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': partition_usage.total,
                        'used': partition_usage.used,
                        'free': partition_usage.free
                    })
                except:
                    continue
            
            # Platform-specific disk detection
            if self.system == 'linux':
                storage_info['disks'] = await self._detect_linux_disks()
            elif self.system == 'windows':
                storage_info['disks'] = await self._detect_windows_disks()
            elif self.system == 'darwin':
                storage_info['disks'] = await self._detect_macos_disks()
                
        except Exception as e:
            self.logger.debug(f"Error detecting storage: {e}")
        
        return storage_info
    
    async def _detect_network_interfaces(self) -> Dict[str, Any]:
        """Detect network interfaces"""
        import psutil
        import netifaces
        
        network_info = {
            'interfaces': [],
            'wireless': [],
            'bluetooth': []
        }
        
        try:
            # Get interface information from psutil
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for interface_name in netifaces.interfaces():
                interface_info = {
                    'name': interface_name,
                    'addresses': [],
                    'is_up': False,
                    'speed': 0,
                    'mtu': 0
                }
                
                # Get addresses
                if interface_name in net_if_addrs:
                    for addr in net_if_addrs[interface_name]:
                        interface_info['addresses'].append({
                            'family': str(addr.family),
                            'address': addr.address,
                            'netmask': addr.netmask,
                            'broadcast': addr.broadcast
                        })
                
                # Get stats
                if interface_name in net_if_stats:
                    stats = net_if_stats[interface_name]
                    interface_info.update({
                        'is_up': stats.isup,
                        'speed': stats.speed,
                        'mtu': stats.mtu,
                        'duplex': str(stats.duplex)
                    })
                
                # Detect interface type
                if 'wl' in interface_name or 'wifi' in interface_name.lower():
                    network_info['wireless'].append(interface_info)
                elif 'bluetooth' in interface_name.lower() or 'bt' in interface_name:
                    network_info['bluetooth'].append(interface_info)
                else:
                    network_info['interfaces'].append(interface_info)
                    
        except Exception as e:
            self.logger.debug(f"Error detecting network interfaces: {e}")
        
        return network_info
    
    async def _detect_motherboard(self) -> Dict[str, Any]:
        """Detect motherboard information"""
        motherboard_info = {}
        
        try:
            if self.system == 'linux':
                try:
                    result = subprocess.run(['dmidecode', '-t', 'baseboard'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        motherboard_info = self._parse_dmidecode_baseboard(result.stdout)
                except:
                    pass
                    
            elif self.system == 'windows':
                try:
                    result = subprocess.run([
                        'wmic', 'baseboard', 'get', 'Manufacturer,Product,Version', '/format:csv'
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        motherboard_info = self._parse_wmic_baseboard(result.stdout)
                except:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Error detecting motherboard: {e}")
        
        return motherboard_info
    
    async def _detect_accelerators(self) -> Dict[str, Any]:
        """Detect specialized accelerators"""
        accelerators = {
            'fpga': [],
            'crypto': [],
            'ai': [],
            'other': []
        }
        
        try:
            if self.system == 'linux':
                # Check for various accelerator devices
                accel_paths = ['/dev/accel*', '/dev/intel-fpga*', '/dev/xdma*']
                for path_pattern in accel_paths:
                    import glob
                    devices = glob.glob(path_pattern)
                    for device in devices:
                        accelerators['other'].append({
                            'device': device,
                            'type': 'unknown'
                        })
                        
        except Exception as e:
            self.logger.debug(f"Error detecting accelerators: {e}")
        
        return accelerators
    
    async def _detect_available_sensors(self) -> Dict[str, Any]:
        """Detect available sensor capabilities"""
        sensors = {
            'temperature': False,
            'fan_speed': False,
            'voltage': False,
            'power': False,
            'humidity': False
        }
        
        try:
            if self.system == 'linux':
                # Check for lm-sensors
                try:
                    subprocess.run(['sensors', '--version'], capture_output=True, check=True)
                    sensors.update({
                        'temperature': True,
                        'fan_speed': True,
                        'voltage': True
                    })
                except:
                    pass
                    
            elif self.system == 'windows':
                # Check for WMI sensor support
                try:
                    import wmi
                    sensors.update({
                        'temperature': True,
                        'fan_speed': True
                    })
                except:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Error detecting sensors: {e}")
        
        return sensors
    
    async def _detect_system_capabilities(self) -> Dict[str, Any]:
        """Detect system capabilities and features"""
        capabilities = {
            'virtualization': False,
            'containers': False,
            'secure_boot': False,
            'tpm': False,
            'uefi': False
        }
        
        try:
            if self.system == 'linux':
                # Check for virtualization
                if os.path.exists('/proc/cpuinfo'):
                    with open('/proc/cpuinfo', 'r') as f:
                        content = f.read()
                        if 'vmx' in content or 'svm' in content:
                            capabilities['virtualization'] = True
                
                # Check for containers
                capabilities['containers'] = (
                    os.path.exists('/usr/bin/docker') or 
                    os.path.exists('/usr/bin/podman')
                )
                
        except Exception as e:
            self.logger.debug(f"Error detecting capabilities: {e}")
        
        return capabilities
    
    # Helper methods for parsing various outputs
    def _parse_dmidecode_memory(self, output: str) -> List[Dict[str, Any]]:
        """Parse dmidecode memory output"""
        modules = []
        current_module = {}
        
        for line in output.split('\n'):
            line = line.strip()
            if 'Memory Device' in line:
                if current_module:
                    modules.append(current_module)
                current_module = {}
            elif ':' in line:
                key, value = line.split(':', 1)
                current_module[key.strip().lower().replace(' ', '_')] = value.strip()
        
        if current_module:
            modules.append(current_module)
        
        return modules
    
    def _get_compute_capability(self, handle) -> str:
        """Get NVIDIA GPU compute capability"""
        try:
            major = pynvml.nvmlDeviceGetCudaComputeCapability(handle)[0]
            minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)[1]
            return f"{major}.{minor}"
        except:
            return "Unknown"
    
    def _get_power_limit(self, handle) -> int:
        """Get NVIDIA GPU power limit"""
        try:
            return pynvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)[1] // 1000
        except:
            return 0