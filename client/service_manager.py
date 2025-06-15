"""
Service management utilities for Master Dashboard Agent
Handles starting, stopping, and managing the agent service across platforms
"""
import os
import sys
import platform
import subprocess
import psutil
from pathlib import Path
import json
import time

class ServiceManager:
    """Cross-platform service management"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.service_name = "MasterDashboardAgent" if self.system == "windows" else "master-dashboard-agent"
    
    def is_service_installed(self) -> bool:
        """Check if service is installed"""
        if self.system == "windows":
            try:
                result = subprocess.run(
                    ["sc", "query", self.service_name],
                    capture_output=True, text=True
                )
                return result.returncode == 0
            except:
                return False
        else:
            service_file = Path(f"/etc/systemd/system/{self.service_name}.service")
            return service_file.exists()
    
    def is_service_running(self) -> bool:
        """Check if service is running"""
        if self.system == "windows":
            try:
                result = subprocess.run(
                    ["sc", "query", self.service_name],
                    capture_output=True, text=True
                )
                return "RUNNING" in result.stdout
            except:
                return False
        else:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", self.service_name],
                    capture_output=True, text=True
                )
                return result.stdout.strip() == "active"
            except:
                return False
    
    def start_service(self):
        """Start the agent service"""
        if not self.is_service_installed():
            raise RuntimeError("Service is not installed")
        
        if self.is_service_running():
            print("Service is already running")
            return
        
        try:
            if self.system == "windows":
                subprocess.check_call(["sc", "start", self.service_name])
            else:
                subprocess.check_call(["systemctl", "start", self.service_name])
            
            # Wait for service to start
            time.sleep(2)
            
            if self.is_service_running():
                print("✓ Service started successfully")
            else:
                raise RuntimeError("Service failed to start")
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to start service: {e}")
    
    def stop_service(self):
        """Stop the agent service"""
        if not self.is_service_running():
            print("Service is not running")
            return
        
        try:
            if self.system == "windows":
                subprocess.check_call(["sc", "stop", self.service_name])
            else:
                subprocess.check_call(["systemctl", "stop", self.service_name])
            
            # Wait for service to stop
            time.sleep(2)
            
            if not self.is_service_running():
                print("✓ Service stopped successfully")
            else:
                print("⚠ Service may still be running")
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to stop service: {e}")
    
    def restart_service(self):
        """Restart the agent service"""
        print("Restarting service...")
        self.stop_service()
        time.sleep(1)
        self.start_service()
    
    def get_service_status(self) -> dict:
        """Get detailed service status"""
        status = {
            "installed": self.is_service_installed(),
            "running": False,
            "pid": None,
            "uptime": None,
            "memory_usage": None,
            "cpu_usage": None
        }
        
        if status["installed"]:
            status["running"] = self.is_service_running()
            
            if status["running"]:
                # Try to find the process
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'memory_info', 'cpu_percent']):
                    try:
                        if any('agent.py' in str(cmd) for cmd in proc.info['cmdline'] or []):
                            status["pid"] = proc.info['pid']
                            status["uptime"] = time.time() - proc.info['create_time']
                            status["memory_usage"] = proc.info['memory_info'].rss / 1024 / 1024  # MB
                            status["cpu_usage"] = proc.info['cpu_percent']
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
        
        return status
    
    def get_service_logs(self, lines: int = 50) -> str:
        """Get service logs"""
        if not self.is_service_installed():
            return "Service is not installed"
        
        try:
            if self.system == "windows":
                # Windows Event Log (simplified)
                return "Windows event logs require additional tools to parse"
            else:
                result = subprocess.run(
                    ["journalctl", "-u", self.service_name, "-n", str(lines), "--no-pager"],
                    capture_output=True, text=True
                )
                return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Failed to get logs: {e}"
    
    def enable_service(self):
        """Enable service to start on boot"""
        if not self.is_service_installed():
            raise RuntimeError("Service is not installed")
        
        try:
            if self.system == "windows":
                subprocess.check_call(["sc", "config", self.service_name, "start=", "auto"])
            else:
                subprocess.check_call(["systemctl", "enable", self.service_name])
            
            print("✓ Service enabled for auto-start")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to enable service: {e}")
    
    def disable_service(self):
        """Disable service auto-start"""
        if not self.is_service_installed():
            print("Service is not installed")
            return
        
        try:
            if self.system == "windows":
                subprocess.check_call(["sc", "config", self.service_name, "start=", "disabled"])
            else:
                subprocess.check_call(["systemctl", "disable", self.service_name])
            
            print("✓ Service disabled from auto-start")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to disable service: {e}")

def main():
    """CLI interface for service management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Master Dashboard Agent Service Manager")
    parser.add_argument("action", choices=[
        "start", "stop", "restart", "status", "logs", "enable", "disable"
    ], help="Action to perform")
    parser.add_argument("--lines", type=int, default=50, help="Number of log lines to show")
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    try:
        if args.action == "start":
            manager.start_service()
        elif args.action == "stop":
            manager.stop_service()
        elif args.action == "restart":
            manager.restart_service()
        elif args.action == "status":
            status = manager.get_service_status()
            print(json.dumps(status, indent=2))
        elif args.action == "logs":
            logs = manager.get_service_logs(args.lines)
            print(logs)
        elif args.action == "enable":
            manager.enable_service()
        elif args.action == "disable":
            manager.disable_service()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()