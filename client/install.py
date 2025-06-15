#!/usr/bin/env python3
"""
Installation script for Master Dashboard Agent
Handles cross-platform installation, service setup, and configuration
"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import json
import getpass
import argparse

class AgentInstaller:
    """Agent installation manager"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.script_dir = Path(__file__).parent
        self.install_dir = self._get_install_dir()
        self.config_dir = self._get_config_dir()
        self.log_dir = self._get_log_dir()
        
    def _get_install_dir(self) -> Path:
        """Get installation directory based on platform"""
        if self.system == "windows":
            return Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "MasterDashboardAgent"
        else:
            return Path("/opt/master-dashboard-agent")
    
    def _get_config_dir(self) -> Path:
        """Get configuration directory based on platform"""
        if self.system == "windows":
            return Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "MasterDashboardAgent"
        else:
            return Path("/etc/master-dashboard-agent")
    
    def _get_log_dir(self) -> Path:
        """Get log directory based on platform"""
        if self.system == "windows":
            return self.config_dir / "logs"
        else:
            return Path("/var/log/master-dashboard-agent")
    
    def check_permissions(self):
        """Check if running with appropriate permissions"""
        if self.system == "windows":
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                raise PermissionError("Installation requires administrator privileges")
        else:
            if os.geteuid() != 0:
                raise PermissionError("Installation requires root privileges")
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("Installing Python dependencies...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.script_dir / "requirements.txt")
            ])
            print("✓ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install dependencies: {e}")
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [self.install_dir, self.config_dir, self.log_dir]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {directory}")
    
    def copy_files(self):
        """Copy agent files to installation directory"""
        print("Copying agent files...")
        
        # Files to copy
        files_to_copy = [
            "agent.py",
            "requirements.txt",
            "collectors/",
            "communication/",
            "utils/",
        ]
        
        for item in files_to_copy:
            src = self.script_dir / item
            dst = self.install_dir / item
            
            if src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"✓ Copied {item}")
            elif src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"✓ Copied directory {item}")
    
    def create_config(self, server_url: str, api_key: str):
        """Create configuration file"""
        config_path = self.config_dir / "config.yaml"
        
        # Copy default config and customize
        default_config = self.script_dir / "config.yaml"
        shutil.copy2(default_config, config_path)
        
        # Update with user-provided values
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        config['server']['url'] = server_url
        config['server']['websocket_url'] = server_url.replace('http', 'ws') + '/ws'
        config['authentication']['api_key'] = api_key
        config['logging']['file'] = str(self.log_dir / "agent.log")
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"✓ Configuration created: {config_path}")
    
    def install_service(self):
        """Install agent as system service"""
        if self.system == "windows":
            self._install_windows_service()
        else:
            self._install_systemd_service()
    
    def _install_windows_service(self):
        """Install Windows service"""
        service_script = self.install_dir / "windows" / "service.py"
        
        try:
            # Install service using pywin32
            subprocess.check_call([
                sys.executable, str(service_script), "install"
            ])
            print("✓ Windows service installed")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install Windows service: {e}")
    
    def _install_systemd_service(self):
        """Install systemd service on Linux"""
        service_file = self.script_dir / "systemd" / "master-dashboard-agent.service"
        systemd_dir = Path("/etc/systemd/system")
        
        # Customize service file
        with open(service_file, 'r') as f:
            service_content = f.read()
        
        service_content = service_content.replace(
            "/opt/master-dashboard-agent", str(self.install_dir)
        ).replace(
            "/etc/master-dashboard-agent", str(self.config_dir)
        )
        
        # Write service file
        service_path = systemd_dir / "master-dashboard-agent.service"
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        # Enable and start service
        subprocess.check_call(["systemctl", "daemon-reload"])
        subprocess.check_call(["systemctl", "enable", "master-dashboard-agent"])
        
        print("✓ Systemd service installed and enabled")
    
    def start_service(self):
        """Start the agent service"""
        if self.system == "windows":
            subprocess.check_call(["sc", "start", "MasterDashboardAgent"])
        else:
            subprocess.check_call(["systemctl", "start", "master-dashboard-agent"])
        
        print("✓ Agent service started")
    
    def install(self, server_url: str, api_key: str):
        """Complete installation process"""
        print("Installing Master Dashboard Agent...")
        print(f"Target platform: {platform.platform()}")
        
        try:
            self.check_permissions()
            self.create_directories()
            self.install_dependencies()
            self.copy_files()
            self.create_config(server_url, api_key)
            self.install_service()
            self.start_service()
            
            print("\n🎉 Installation completed successfully!")
            print(f"Installation directory: {self.install_dir}")
            print(f"Configuration file: {self.config_dir / 'config.yaml'}")
            print(f"Log directory: {self.log_dir}")
            
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Master Dashboard Agent Installer")
    parser.add_argument("--server-url", required=True, help="Master Dashboard server URL")
    parser.add_argument("--api-key", required=True, help="API key for authentication")
    parser.add_argument("--no-service", action="store_true", help="Don't install as service")
    
    args = parser.parse_args()
    
    installer = AgentInstaller()
    installer.install(args.server_url, args.api_key)

if __name__ == "__main__":
    main()