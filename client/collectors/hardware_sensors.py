"""
Hardware sensors collector for Master Dashboard Agent
Detects and monitors hardware sensors including temperature, fan speeds, voltages
with cross-platform support and automatic hardware detection
"""
import asyncio
import platform
import subprocess
import json
import logging
from typing import Dict, Any, Optional, List
import os

try:
    import pynvml
    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False

class HardwareSensorsCollector:
    """Collects hardware sensor data with automatic detection"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.system = platform.system().lower()
        self.nvidia_initialized = False
        self.sensors_available = self._check_sensors_availability()
        
    def _check_sensors_availability(self) -> Dict[str, bool]:
        """Check what sensor tools are available"""
        availability = {
            'lm_sensors': False,
            'nvidia_ml': False,
            'wmi': False,
            'smc': False
        }
        
        if self.system == 'linux':
            # Check for lm-sensors
            try:
                subprocess.run(['sensors', '--version'], 
                             capture_output=True, check=True)
                availability['lm_sensors'] = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
                
        elif self.system == 'windows':
            # Check for WMI
            try:
                import wmi
                availability['wmi'] = True
            except ImportError:
                pass
                
        elif self.system == 'darwin':
            # Check for powermetrics (macOS)
            try:
                subprocess.run(['powermetrics', '--help'], 
                             capture_output=True, check=True)
                availability['smc'] = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # Check NVIDIA
        if NVIDIA_AVAILABLE:
            try:
                pynvml.nvmlInit()
                availability['nvidia_ml'] = True
                self.nvidia_initialized = True
            except Exception as e:
                self.logger.debug(f"NVIDIA ML not available: {e}")
        
        return availability
    
    async def collect(self) -> Dict[str, Any]:
        """Collect all available hardware sensor data"""
        try:
            sensors_data = {
                'timestamp': asyncio.get_event_loop().time(),
                'temperature': await self._collect_temperature(),
                'fan_speeds': await self._collect_fan_speeds(),
                'voltages': await self._collect_voltages(),
                'gpu': await self._collect_gpu_sensors(),
                'power': await self._collect_power_info()
            }
            return sensors_data
        except Exception as e:
            self.logger.error(f"Error collecting hardware sensors: {e}")
            return {'error': str(e)}
    
    async def _collect_temperature(self) -> Dict[str, Any]:
        """Collect temperature sensors"""
        temperatures = {}
        
        if self.system == 'linux' and self.sensors_available['lm_sensors']:
            temperatures.update(await self._collect_linux_temperatures())
        elif self.system == 'windows' and self.sensors_available['wmi']:
            temperatures.update(await self._collect_windows_temperatures())
        elif self.system == 'darwin' and self.sensors_available['smc']:
            temperatures.update(await self._collect_macos_temperatures())
        
        return temperatures
    
    async def _collect_linux_temperatures(self) -> Dict[str, Any]:
        """Collect temperatures on Linux using lm-sensors"""
        temps = {}
        try:
            result = subprocess.run(['sensors', '-A', '-j'], 
                                  capture_output=True, text=True, check=True)
            sensors_data = json.loads(result.stdout)
            
            for chip_name, chip_data in sensors_data.items():
                if isinstance(chip_data, dict):
                    for sensor_name, sensor_data in chip_data.items():
                        if isinstance(sensor_data, dict) and 'temp' in sensor_name.lower():
                            for key, value in sensor_data.items():
                                if 'input' in key and isinstance(value, (int, float)):
                                    temps[f"{chip_name}_{sensor_name}"] = {
                                        'current': value,
                                        'unit': 'celsius'
                                    }
        except Exception as e:
            self.logger.debug(f"Cannot get Linux temperatures: {e}")
        
        return temps
    
    async def _collect_windows_temperatures(self) -> Dict[str, Any]:
        """Collect temperatures on Windows using WMI"""
        temps = {}
        try:
            import wmi
            c = wmi.WMI(namespace="root\\wmi")
            
            # Try different WMI classes for temperature
            temp_classes = [
                'MSAcpi_ThermalZoneTemperature',
                'Win32_TemperatureProbe'
            ]
            
            for temp_class in temp_classes:
                try:
                    temp_sensors = getattr(c, temp_class)()
                    for i, sensor in enumerate(temp_sensors):
                        if hasattr(sensor, 'CurrentTemperature'):
                            # Convert from tenths of Kelvin to Celsius
                            temp_celsius = (sensor.CurrentTemperature / 10.0) - 273.15
                            temps[f"thermal_zone_{i}"] = {
                                'current': temp_celsius,
                                'unit': 'celsius'
                            }
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Cannot get Windows temperatures: {e}")
        
        return temps
    
    async def _collect_macos_temperatures(self) -> Dict[str, Any]:
        """Collect temperatures on macOS using powermetrics"""
        temps = {}
        try:
            result = subprocess.run([
                'powermetrics', '--samplers', 'smc', '-n', '1', '--format', 'plist'
            ], capture_output=True, text=True, check=True)
            
            # Parse plist output (simplified)
            if 'CPU die temperature' in result.stdout:
                # Extract temperature values using basic parsing
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'temperature' in line.lower():
                        # Basic extraction - would need plistlib for proper parsing
                        temps['cpu_temp'] = {
                            'current': 0.0,  # Placeholder
                            'unit': 'celsius'
                        }
                        break
        except Exception as e:
            self.logger.debug(f"Cannot get macOS temperatures: {e}")
        
        return temps
    
    async def _collect_fan_speeds(self) -> Dict[str, Any]:
        """Collect fan speed data"""
        fans = {}
        
        if self.system == 'linux' and self.sensors_available['lm_sensors']:
            try:
                result = subprocess.run(['sensors', '-A', '-j'], 
                                      capture_output=True, text=True, check=True)
                sensors_data = json.loads(result.stdout)
                
                for chip_name, chip_data in sensors_data.items():
                    if isinstance(chip_data, dict):
                        for sensor_name, sensor_data in chip_data.items():
                            if isinstance(sensor_data, dict) and 'fan' in sensor_name.lower():
                                for key, value in sensor_data.items():
                                    if 'input' in key and isinstance(value, (int, float)):
                                        fans[f"{chip_name}_{sensor_name}"] = {
                                            'rpm': value,
                                            'unit': 'rpm'
                                        }
            except Exception as e:
                self.logger.debug(f"Cannot get fan speeds: {e}")
        
        return fans
    
    async def _collect_voltages(self) -> Dict[str, Any]:
        """Collect voltage data"""
        voltages = {}
        
        if self.system == 'linux' and self.sensors_available['lm_sensors']:
            try:
                result = subprocess.run(['sensors', '-A', '-j'], 
                                      capture_output=True, text=True, check=True)
                sensors_data = json.loads(result.stdout)
                
                for chip_name, chip_data in sensors_data.items():
                    if isinstance(chip_data, dict):
                        for sensor_name, sensor_data in chip_data.items():
                            if isinstance(sensor_data, dict) and 'in' in sensor_name.lower():
                                for key, value in sensor_data.items():
                                    if 'input' in key and isinstance(value, (int, float)):
                                        voltages[f"{chip_name}_{sensor_name}"] = {
                                            'voltage': value,
                                            'unit': 'volts'
                                        }
            except Exception as e:
                self.logger.debug(f"Cannot get voltages: {e}")
        
        return voltages
    
    async def _collect_gpu_sensors(self) -> Dict[str, Any]:
        """Collect GPU sensor data"""
        gpu_data = {}
        
        if self.nvidia_initialized:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle).decode()
                    
                    gpu_info = {
                        'name': name,
                        'index': i
                    }
                    
                    # Temperature
                    try:
                        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                        gpu_info['temperature'] = {'current': temp, 'unit': 'celsius'}
                    except:
                        pass
                    
                    # Fan speed
                    try:
                        fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
                        gpu_info['fan_speed'] = {'percent': fan_speed, 'unit': 'percent'}
                    except:
                        pass
                    
                    # Power usage
                    try:
                        power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                        gpu_info['power'] = {'current': power, 'unit': 'watts'}
                    except:
                        pass
                    
                    # Clock speeds
                    try:
                        graphics_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
                        memory_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
                        gpu_info['clocks'] = {
                            'graphics': graphics_clock,
                            'memory': memory_clock,
                            'unit': 'MHz'
                        }
                    except:
                        pass
                    
                    gpu_data[f"gpu_{i}"] = gpu_info
                    
            except Exception as e:
                self.logger.debug(f"Cannot get NVIDIA GPU sensors: {e}")
        
        return gpu_data
    
    async def _collect_power_info(self) -> Dict[str, Any]:
        """Collect power consumption information"""
        power_data = {}
        
        if self.system == 'linux':
            # Check for battery information
            try:
                battery_path = '/sys/class/power_supply'
                if os.path.exists(battery_path):
                    for battery in os.listdir(battery_path):
                        battery_dir = os.path.join(battery_path, battery)
                        if os.path.isdir(battery_dir):
                            battery_info = {}
                            
                            # Read battery files
                            for file_name in ['capacity', 'status', 'voltage_now', 'current_now']:
                                file_path = os.path.join(battery_dir, file_name)
                                if os.path.exists(file_path):
                                    try:
                                        with open(file_path, 'r') as f:
                                            value = f.read().strip()
                                            if file_name == 'capacity':
                                                battery_info['capacity_percent'] = int(value)
                                            elif file_name == 'status':
                                                battery_info['status'] = value
                                            elif file_name == 'voltage_now':
                                                battery_info['voltage'] = int(value) / 1000000  # Convert to volts
                                            elif file_name == 'current_now':
                                                battery_info['current'] = int(value) / 1000000  # Convert to amps
                                    except:
                                        pass
                            
                            if battery_info:
                                power_data[battery] = battery_info
            except Exception as e:
                self.logger.debug(f"Cannot get Linux power info: {e}")
        
        return power_data