#!/usr/bin/env python3
"""
Shared Utilities Module
Common utility functions and classes for Master Dashboard agents
"""

import hashlib
import json
import logging
import os
import platform
import socket
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from logging.handlers import RotatingFileHandler

def setup_logging(log_file: str = None, log_level: str = "INFO", max_size: str = "10MB", backup_count: int = 5) -> logging.Logger:
    """Setup logging configuration for the agent"""
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            # Convert max_size to bytes
            max_bytes = parse_size_string(max_size)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")
    
    return logger

def load_config(config_path: str, default_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load configuration from JSON file with fallback to defaults"""
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        else:
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
    except Exception as e:
        if default_config:
            return default_config
        else:
            # Return minimal default configuration
            return {
                "server": {
                    "url": "http://localhost:8000",
                    "api_key": None,
                    "timeout": 30
                },
                "collection_interval": 5,
                "logging": {
                    "level": "INFO"
                }
            }

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """Save configuration to JSON file"""
    
    try:
        # Create directory if it doesn't exist
        config_dir = os.path.dirname(config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to save config: {e}")
        return False

def create_machine_info() -> Dict[str, Any]:
    """Create comprehensive machine information for registration"""
    
    try:
        # Generate unique machine ID based on hardware characteristics
        machine_id = generate_machine_id()
        
        # Get system information
        system_info = {
            "id": machine_id,
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "ip_addresses": get_ip_addresses(),
            "mac_addresses": get_mac_addresses(),
            "boot_time": get_boot_time(),
            "registration_time": datetime.utcnow().isoformat()
        }
        
        # Add OS-specific information
        if platform.system().lower() == "windows":
            system_info.update(get_windows_info())
        elif platform.system().lower() == "linux":
            system_info.update(get_linux_info())
        elif platform.system().lower() == "darwin":
            system_info.update(get_macos_info())
        
        return system_info
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error creating machine info: {e}")
        return {
            "id": str(uuid.uuid4()),
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "error": str(e)
        }

def generate_machine_id() -> str:
    """Generate a unique, consistent machine ID"""
    
    try:
        # Collect hardware identifiers
        identifiers = []
        
        # Hostname
        identifiers.append(socket.gethostname())
        
        # MAC addresses
        mac_addresses = get_mac_addresses()
        if mac_addresses:
            identifiers.extend(sorted(mac_addresses))
        
        # Platform information
        identifiers.extend([
            platform.system(),
            platform.machine(),
            platform.processor()
        ])
        
        # Create hash from identifiers
        combined = "|".join(str(i) for i in identifiers if i)
        machine_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
        # Return first 16 characters as machine ID
        return machine_hash[:16]
        
    except Exception:
        # Fallback to UUID if hardware ID generation fails
        return str(uuid.uuid4()).replace('-', '')[:16]

def get_ip_addresses() -> list:
    """Get all IP addresses for the machine"""
    
    ip_addresses = []
    
    try:
        import socket
        
        # Get local IP addresses
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip and local_ip != "127.0.0.1":
            ip_addresses.append(local_ip)
        
        # Try alternative method for better IP detection
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip_addresses.append(s.getsockname()[0])
        except Exception:
            pass
            
    except Exception:
        pass
    
    # Remove duplicates and loopback
    unique_ips = list(set(ip_addresses))
    return [ip for ip in unique_ips if ip != "127.0.0.1"]

def get_mac_addresses() -> list:
    """Get MAC addresses for network interfaces"""
    
    mac_addresses = []
    
    try:
        import psutil
        
        # Get network interfaces
        interfaces = psutil.net_if_addrs()
        
        for interface_name, addresses in interfaces.items():
            for address in addresses:
                if address.family == psutil.AF_LINK:  # MAC address
                    mac = address.address
                    if mac and mac != "00:00:00:00:00:00":
                        mac_addresses.append(mac)
                        
    except ImportError:
        # Fallback method without psutil
        try:
            import uuid
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0,2*6,2)][::-1])
            if mac != "00:00:00:00:00:00":
                mac_addresses.append(mac)
        except Exception:
            pass
    except Exception:
        pass
    
    return list(set(mac_addresses))

def get_boot_time() -> Optional[str]:
    """Get system boot time"""
    
    try:
        import psutil
        boot_timestamp = psutil.boot_time()
        boot_time = datetime.fromtimestamp(boot_timestamp)
        return boot_time.isoformat()
    except Exception:
        return None

def get_windows_info() -> Dict[str, Any]:
    """Get Windows-specific system information"""
    
    info = {}
    
    try:
        import platform
        
        # Windows version details
        info["windows_version"] = platform.win32_ver()
        
        # Try to get additional Windows info via WMI
        try:
            import wmi
            c = wmi.WMI()
            
            # Computer system info
            for system in c.Win32_ComputerSystem():
                info.update({
                    "manufacturer": system.Manufacturer,
                    "model": system.Model,
                    "total_physical_memory": system.TotalPhysicalMemory
                })
                break
                
            # Operating system info
            for os_info in c.Win32_OperatingSystem():
                info.update({
                    "os_name": os_info.Name,
                    "os_version": os_info.Version,
                    "service_pack": os_info.ServicePackMajorVersion
                })
                break
                
        except ImportError:
            pass
        except Exception:
            pass
            
    except Exception:
        pass
    
    return info

def get_linux_info() -> Dict[str, Any]:
    """Get Linux-specific system information"""
    
    info = {}
    
    try:
        # Distribution information
        try:
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                
            os_release = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os_release[key] = value.strip('"')
                    
            info["distribution"] = os_release.get("NAME", "Unknown")
            info["distribution_version"] = os_release.get("VERSION", "Unknown")
            info["distribution_id"] = os_release.get("ID", "Unknown")
            
        except Exception:
            pass
        
        # Kernel information
        info["kernel_version"] = platform.release()
        
        # CPU information
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                
            # Extract CPU model
            for line in cpuinfo.split('\n'):
                if line.startswith('model name'):
                    info["cpu_model"] = line.split(':', 1)[1].strip()
                    break
                    
        except Exception:
            pass
            
    except Exception:
        pass
    
    return info

def get_macos_info() -> Dict[str, Any]:
    """Get macOS-specific system information"""
    
    info = {}
    
    try:
        import subprocess
        
        # macOS version
        try:
            result = subprocess.run(['sw_vers', '-productVersion'], 
                                 capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                info["macos_version"] = result.stdout.strip()
        except Exception:
            pass
        
        # Hardware information
        try:
            result = subprocess.run(['system_profiler', 'SPHardwareDataType'], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                output = result.stdout
                
                # Parse hardware info
                for line in output.split('\n'):
                    line = line.strip()
                    if 'Model Name:' in line:
                        info["model_name"] = line.split(':', 1)[1].strip()
                    elif 'Model Identifier:' in line:
                        info["model_identifier"] = line.split(':', 1)[1].strip()
                    elif 'Processor Name:' in line:
                        info["processor_name"] = line.split(':', 1)[1].strip()
                        
        except Exception:
            pass
            
    except Exception:
        pass
    
    return info

def parse_size_string(size_str: str) -> int:
    """Parse size string (e.g., '10MB', '1GB') to bytes"""
    
    size_str = size_str.upper().strip()
    
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4
    }
    
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            try:
                number = float(size_str[:-len(suffix)])
                return int(number * multiplier)
            except ValueError:
                break
    
    # Default to 10MB if parsing fails
    return 10 * 1024 * 1024

def validate_server_url(url: str) -> bool:
    """Validate server URL format"""
    
    try:
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        
        # Check if URL has scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Check if scheme is http or https
        if parsed.scheme not in ['http', 'https']:
            return False
        
        return True
        
    except Exception:
        return False

def format_bytes(bytes_value: Union[int, float]) -> str:
    """Format bytes value to human readable string"""
    
    try:
        bytes_value = float(bytes_value)
        
        if bytes_value < 1024:
            return f"{bytes_value:.1f} B"
        elif bytes_value < 1024 ** 2:
            return f"{bytes_value / 1024:.1f} KB"
        elif bytes_value < 1024 ** 3:
            return f"{bytes_value / (1024 ** 2):.1f} MB"
        elif bytes_value < 1024 ** 4:
            return f"{bytes_value / (1024 ** 3):.1f} GB"
        else:
            return f"{bytes_value / (1024 ** 4):.1f} TB"
            
    except (ValueError, TypeError):
        return "0 B"

def format_percentage(value: Union[int, float], decimals: int = 1) -> str:
    """Format percentage value"""
    
    try:
        return f"{float(value):.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.0%"

def ensure_directory(path: str) -> bool:
    """Ensure directory exists, create if necessary"""
    
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to create directory {path}: {e}")
        return False

def is_admin() -> bool:
    """Check if running with administrator/root privileges"""
    
    try:
        if platform.system().lower() == "windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def get_current_user() -> str:
    """Get current username"""
    
    try:
        import getpass
        return getpass.getuser()
    except Exception:
        return "unknown"

class ConfigValidator:
    """Configuration validation utilities"""
    
    @staticmethod
    def validate_server_config(config: Dict[str, Any]) -> tuple[bool, list]:
        """Validate server configuration"""
        
        errors = []
        
        # Check required server fields
        if 'server' not in config:
            errors.append("Missing 'server' section")
            return False, errors
        
        server_config = config['server']
        
        if 'url' not in server_config:
            errors.append("Missing server URL")
        elif not validate_server_url(server_config['url']):
            errors.append("Invalid server URL format")
        
        # Validate timeout
        if 'timeout' in server_config:
            try:
                timeout = int(server_config['timeout'])
                if timeout <= 0:
                    errors.append("Timeout must be positive")
            except (ValueError, TypeError):
                errors.append("Timeout must be a number")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_metrics_config(config: Dict[str, Any]) -> tuple[bool, list]:
        """Validate metrics configuration"""
        
        errors = []
        
        # Check collection interval
        if 'collection_interval' in config:
            try:
                interval = int(config['collection_interval'])
                if interval <= 0:
                    errors.append("Collection interval must be positive")
                elif interval < 1:
                    errors.append("Collection interval should be at least 1 second")
            except (ValueError, TypeError):
                errors.append("Collection interval must be a number")
        
        return len(errors) == 0, errors

def create_pid_file(pid_file_path: str) -> bool:
    """Create PID file for the agent process"""
    
    try:
        pid = os.getpid()
        
        # Create directory if necessary
        pid_dir = os.path.dirname(pid_file_path)
        if pid_dir:
            ensure_directory(pid_dir)
        
        with open(pid_file_path, 'w') as f:
            f.write(str(pid))
        
        return True
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to create PID file: {e}")
        return False

def remove_pid_file(pid_file_path: str) -> bool:
    """Remove PID file"""
    
    try:
        if os.path.exists(pid_file_path):
            os.remove(pid_file_path)
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to remove PID file: {e}")
        return False

def check_process_running(pid_file_path: str) -> bool:
    """Check if process is running based on PID file"""
    
    try:
        if not os.path.exists(pid_file_path):
            return False
        
        with open(pid_file_path, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            # Process doesn't exist, remove stale PID file
            remove_pid_file(pid_file_path)
            return False
            
    except Exception:
        return False