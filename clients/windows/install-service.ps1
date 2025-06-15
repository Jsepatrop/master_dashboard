# Master Dashboard Windows Service Installation Helper
# This script provides additional service management utilities

param(
    [string]$Action = "help",
    [string]$ServiceName = "MasterDashboardAgent",
    [string]$InstallPath = "C:\Program Files\MasterDashboard"
)

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Install-Service {
    Write-Info "Installing Windows service..."
    
    try {
        Push-Location $InstallPath
        python agent.py install
        Set-Service -Name $ServiceName -StartupType Automatic
        Pop-Location
        
        Write-Success "Service installed successfully"
        return $true
    } catch {
        Write-Error "Failed to install service: $_"
        if (Test-Path $InstallPath) { Pop-Location }
        return $false
    }
}

function Remove-Service {
    Write-Info "Removing Windows service..."
    
    try {
        # Stop service first
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        
        Push-Location $InstallPath
        python agent.py remove
        Pop-Location
        
        Write-Success "Service removed successfully"
        return $true
    } catch {
        Write-Error "Failed to remove service: $_"
        if (Test-Path $InstallPath) { Pop-Location }
        return $false
    }
}

function Start-AgentService {
    Write-Info "Starting service..."
    
    try {
        Start-Service -Name $ServiceName
        Write-Success "Service started successfully"
        return $true
    } catch {
        Write-Error "Failed to start service: $_"
        return $false
    }
}

function Stop-AgentService {
    Write-Info "Stopping service..."
    
    try {
        Stop-Service -Name $ServiceName -Force
        Write-Success "Service stopped successfully"
        return $true
    } catch {
        Write-Error "Failed to stop service: $_"
        return $false
    }
}

function Get-ServiceStatus {
    Write-Info "Checking service status..."
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        
        if ($service) {
            Write-Host "Service Status: $($service.Status)" -ForegroundColor Cyan
            Write-Host "Startup Type: $((Get-WmiObject -Class Win32_Service -Filter "Name='$ServiceName'").StartMode)" -ForegroundColor Cyan
            return $true
        } else {
            Write-Error "Service not found"
            return $false
        }
    } catch {
        Write-Error "Failed to get service status: $_"
        return $false
    }
}

function Show-ServiceLogs {
    Write-Info "Showing recent service logs..."
    
    try {
        $logPath = "C:\ProgramData\MasterDashboard\logs\agent.log"
        
        if (Test-Path $logPath) {
            Write-Host "Recent log entries:" -ForegroundColor Cyan
            Get-Content $logPath -Tail 20
        } else {
            Write-Warning "Log file not found: $logPath"
        }
        
        return $true
    } catch {
        Write-Error "Failed to read logs: $_"
        return $false
    }
}

# Main logic
switch ($Action.ToLower()) {
    "install" {
        Install-Service
    }
    "remove" {
        Remove-Service
    }
    "start" {
        Start-AgentService
    }
    "stop" {
        Stop-AgentService
    }
    "restart" {
        Stop-AgentService
        Start-Sleep -Seconds 2
        Start-AgentService
    }
    "status" {
        Get-ServiceStatus
    }
    "logs" {
        Show-ServiceLogs
    }
    "help" {
        Write-Host "Master Dashboard Service Management" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Usage: .\install-service.ps1 -Action <action>"
        Write-Host ""
        Write-Host "Actions:"
        Write-Host "  install  - Install the Windows service"
        Write-Host "  remove   - Remove the Windows service"
        Write-Host "  start    - Start the service"
        Write-Host "  stop     - Stop the service"
        Write-Host "  restart  - Restart the service"
        Write-Host "  status   - Show service status"
        Write-Host "  logs     - Show recent log entries"
        Write-Host "  help     - Show this help message"
    }
    default {
        Write-Error "Unknown action: $Action"
        Write-Host "Use -Action help for available actions"
        exit 1
    }
}