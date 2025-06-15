"""
Windows Service wrapper for Master Dashboard Agent
Handles service installation, startup, and management on Windows systems
"""
import sys
import os
import time
import logging
from pathlib import Path
import asyncio
import threading

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

# Add the agent directory to Python path
AGENT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(AGENT_DIR))

from agent import MasterDashboardAgent
from utils.logger import setup_logger

class MasterDashboardService(win32serviceutil.ServiceFramework):
    """Windows service wrapper for Master Dashboard Agent"""
    
    _svc_name_ = "MasterDashboardAgent"
    _svc_display_name_ = "Master Dashboard Agent"
    _svc_description_ = "System monitoring agent for Master Dashboard"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.logger = None
        self.agent = None
        self.agent_thread = None
        self.loop = None
        
    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        
        if self.logger:
            self.logger.info("Service stop requested")
        
        # Stop the agent
        if self.agent and self.loop:
            try:
                future = asyncio.run_coroutine_threadsafe(self.agent.stop(), self.loop)
                future.result(timeout=10)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error stopping agent: {e}")
        
        if self.logger:
            self.logger.info("Service stopped")
    
    def SvcDoRun(self):
        """Main service execution"""
        try:
            # Setup logging
            self.setup_logging()
            self.logger.info("Master Dashboard Agent service starting")
            
            # Log to Windows Event Log
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            # Start the agent in a separate thread
            self.agent_thread = threading.Thread(target=self.run_agent)
            self.agent_thread.daemon = True
            self.agent_thread.start()
            
            # Wait for stop event
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            
            # Wait for agent thread to finish
            if self.agent_thread and self.agent_thread.is_alive():
                self.agent_thread.join(timeout=10)
            
            self.logger.info("Service execution completed")
            
        except Exception as e:
            error_msg = f"Service execution error: {e}"
            if self.logger:
                self.logger.error(error_msg)
            
            # Log to Windows Event Log
            servicemanager.LogErrorMsg(error_msg)
            
            # Set service as stopped with error
            self.ReportServiceStatus(win32service.SERVICE_STOPPED, 1)
    
    def setup_logging(self):
        """Setup service logging"""
        try:
            # Determine log file path
            log_dir = Path(os.environ.get('PROGRAMDATA', 'C:\\ProgramData')) / 'MasterDashboardAgent' / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / 'service.log'
            
            # Setup logger
            self.logger = setup_logger(
                name="master_dashboard_service",
                level="INFO",
                log_file=str(log_file),
                console=False
            )
            
        except Exception as e:
            # Fallback logging to Windows Event Log only
            servicemanager.LogErrorMsg(f"Failed to setup file logging: {e}")
    
    def run_agent(self):
        """Run the agent in async context"""
        try:
            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Determine config file path
            config_dir = Path(os.environ.get('PROGRAMDATA', 'C:\\ProgramData')) / 'MasterDashboardAgent'
            config_file = config_dir / 'config.yaml'
            
            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
            # Create and start agent
            self.agent = MasterDashboardAgent(str(config_file))
            
            if self.logger:
                self.logger.info(f"Starting agent with config: {config_file}")
            
            # Run agent
            self.loop.run_until_complete(self.agent.start())
            
        except Exception as e:
            error_msg = f"Agent execution error: {e}"
            if self.logger:
                self.logger.error(error_msg)
            servicemanager.LogErrorMsg(error_msg)
        finally:
            if self.loop:
                self.loop.close()

def install_service():
    """Install the Windows service"""
    try:
        # Get the Python executable and script path
        python_exe = sys.executable
        script_path = os.path.abspath(__file__)
        
        # Install service
        win32serviceutil.InstallService(
            pythonClassString=f"{__name__}.MasterDashboardService",
            serviceName=MasterDashboardService._svc_name_,
            displayName=MasterDashboardService._svc_display_name_,
            description=MasterDashboardService._svc_description_,
            startType=win32service.SERVICE_AUTO_START,
            exeName=python_exe,
            exeArgs=f'"{script_path}"'
        )
        
        print(f"Service '{MasterDashboardService._svc_display_name_}' installed successfully")
        print("You can start it with: sc start MasterDashboardAgent")
        
    except Exception as e:
        print(f"Failed to install service: {e}")
        return False
    
    return True

def remove_service():
    """Remove the Windows service"""
    try:
        win32serviceutil.RemoveService(MasterDashboardService._svc_name_)
        print(f"Service '{MasterDashboardService._svc_display_name_}' removed successfully")
    except Exception as e:
        print(f"Failed to remove service: {e}")
        return False
    
    return True

def start_service():
    """Start the Windows service"""
    try:
        win32serviceutil.StartService(MasterDashboardService._svc_name_)
        print(f"Service '{MasterDashboardService._svc_display_name_}' started successfully")
    except Exception as e:
        print(f"Failed to start service: {e}")
        return False
    
    return True

def stop_service():
    """Stop the Windows service"""
    try:
        win32serviceutil.StopService(MasterDashboardService._svc_name_)
        print(f"Service '{MasterDashboardService._svc_display_name_}' stopped successfully")
    except Exception as e:
        print(f"Failed to stop service: {e}")
        return False
    
    return True

def main():
    """Main entry point for service management"""
    if not WIN32_AVAILABLE:
        print("ERROR: pywin32 is required for Windows service functionality")
        print("Install with: pip install pywin32")
        sys.exit(1)
    
    if len(sys.argv) == 1:
        # Run as service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MasterDashboardService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Handle command line arguments
        command = sys.argv[1].lower()
        
        if command == 'install':
            install_service()
        elif command == 'remove' or command == 'uninstall':
            remove_service()
        elif command == 'start':
            start_service()
        elif command == 'stop':
            stop_service()
        elif command == 'restart':
            stop_service()
            time.sleep(2)
            start_service()
        else:
            print("Usage:")
            print(f"  {sys.argv[0]} install    - Install service")
            print(f"  {sys.argv[0]} remove     - Remove service")
            print(f"  {sys.argv[0]} start      - Start service")
            print(f"  {sys.argv[0]} stop       - Stop service")
            print(f"  {sys.argv[0]} restart    - Restart service")

if __name__ == '__main__':
    main()