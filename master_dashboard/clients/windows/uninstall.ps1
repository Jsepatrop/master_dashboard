# Master Dashboard Windows Agent Uninstallation Script
# This script removes the Master Dashboard Agent from Windows systems

param(
    [string]$InstallPath = "C:\Program Files\MasterDashboard",
    [string]$ServiceName = "MasterDashboardAgent",
    [switch]$KeepLogs = $false,
    [switch]$Force = $false
)

# Requires Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script requires Administrator privileges. Please run as Administrator."
    exit 1
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Master Dashboard Agent Uninstallation" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Stop-AgentService {
    Write-Info "Stopping Master Dashboard Agent service..."
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        
        if ($service) {
            if ($service.Status -eq "Running") {
                Stop-Service -Name $ServiceName -Force
                Write-Success "Service stopped successfully"
            } else {
                Write-Info "Service was not running"
            }
            return $true
        } else {
            Write-Info "Service not found"
            return $true
        }
    } catch {
        Write-Error "Failed to stop service: $_"
        return $false
    }
}

function Remove-WindowsService {
    Write-Info "Removing Windows service..."
    
    try {
        # Change to installation directory if it exists
        if (Test-Path $InstallPath) {
            Push-Location $InstallPath
            
            try {
                # Remove the service
                python agent.py remove
                Write-Success "Windows service removed successfully"
                $result = $true
            } catch {
                Write-Warning "Could not remove service via Python script: $_"
                # Try alternative method
                sc.exe delete $ServiceName
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Windows service removed successfully (alternative method)"
                    $result = $true
                } else {
                    Write-Error "Failed to remove Windows service"
                    $result = $false
                }
            }
            
            Pop-Location
            return $result
        } else {
            # Try to remove service directly
            sc.exe delete $ServiceName
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Windows service removed successfully"
                return $true
            } else {
                Write-Info "Service may not exist or already removed"
                return $true
            }
        }
    } catch {
        Write-Error "Failed to remove Windows service: $_"
        if (Test-Path $InstallPath) {
            Pop-Location
        }
        return $false
    }
}

function Remove-InstallationFiles {
    Write-Info "Removing installation files..."
    
    try {
        if (Test-Path $InstallPath) {
            Remove-Item $InstallPath -Recurse -Force
            Write-Success "Installation files removed successfully"
        } else {
            Write-Info "Installation directory not found"
        }
        return $true
    } catch {
        Write-Error "Failed to remove installation files: $_"
        return $false
    }
}

function Remove-DataFiles {
    Write-Info "Removing data files..."
    
    try {
        $dataPath = "C:\ProgramData\MasterDashboard"
        
        if (Test-Path $dataPath) {
            if ($KeepLogs) {
                # Remove everything except logs
                $items = Get-ChildItem $dataPath | Where-Object { $_.Name -ne "logs" }
                foreach ($item in $items) {
                    Remove-Item $item.FullName -Recurse -Force
                }
                Write-Success "Data files removed (logs preserved)"
            } else {
                Remove-Item $dataPath -Recurse -Force
                Write-Success "All data files removed"
            }
        } else {
            Write-Info "Data directory not found"
        }
        return $true
    } catch {
        Write-Error "Failed to remove data files: $_"
        return $false
    }
}

function Confirm-Uninstallation {
    if ($Force) {
        return $true
    }
    
    Write-Warning "This will completely remove the Master Dashboard Agent from this system."
    Write-Host "Installation Path: $InstallPath"
    Write-Host "Data Path: C:\ProgramData\MasterDashboard"
    
    if ($KeepLogs) {
        Write-Host "Logs will be preserved in: C:\ProgramData\MasterDashboard\logs"
    }
    
    Write-Host ""
    $confirmation = Read-Host "Are you sure you want to continue? (y/N)"
    
    return ($confirmation -eq "y" -or $confirmation -eq "Y" -or $confirmation -eq "yes" -or $confirmation -eq "Yes")
}

# Main uninstallation process
try {
    Write-Info "Starting Master Dashboard Agent uninstallation..."
    Write-Host ""
    
    # Confirm uninstallation
    if (-not (Confirm-Uninstallation)) {
        Write-Info "Uninstallation cancelled by user"
        exit 0
    }
    
    Write-Host ""
    
    # Stop service
    if (-not (Stop-AgentService)) {
        if (-not $Force) {
            Write-Error "Failed to stop service. Use -Force to continue anyway."
            exit 1
        }
    }
    
    # Remove Windows service
    if (-not (Remove-WindowsService)) {
        if (-not $Force) {
            Write-Error "Failed to remove service. Use -Force to continue anyway."
            exit 1
        }
    }
    
    # Remove installation files
    if (-not (Remove-InstallationFiles)) {
        if (-not $Force) {
            Write-Error "Failed to remove installation files. Use -Force to continue anyway."
            exit 1
        }
    }
    
    # Remove data files
    if (-not (Remove-DataFiles)) {
        if (-not $Force) {
            Write-Error "Failed to remove data files. Use -Force to continue anyway."
            exit 1
        }
    }
    
    Write-Host ""
    Write-Success "🎉 Master Dashboard Agent uninstallation completed!"
    Write-Host ""
    
    if ($KeepLogs) {
        Write-Info "Log files have been preserved in: C:\ProgramData\MasterDashboard\logs"
    }
    
    Write-Info "Thank you for using Master Dashboard Agent."
    
} catch {
    Write-Error "Uninstallation failed: $_"
    exit 1
}