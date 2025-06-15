# Master Dashboard Windows Agent Installation Script
# This script installs the Master Dashboard Agent on Windows systems

param(
    [string]$ServerUrl = "http://localhost:8000",
    [string]$InstallPath = "C:\Program Files\MasterDashboard",
    [string]$ServiceName = "MasterDashboardAgent",
    [switch]$Unattended = $false
)

# Requires Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script requires Administrator privileges. Please run as Administrator."
    exit 1
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Master Dashboard Agent Installation" -ForegroundColor Cyan
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

function Test-PythonInstallation {
    Write-Info "Checking Python installation..."
    
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $majorVersion = [int]$matches[1]
            $minorVersion = [int]$matches[2]
            
            if ($majorVersion -eq 3 -and $minorVersion -ge 8) {
                Write-Success "Python $($matches[0]) found"
                return $true
            } else {
                Write-Error "Python 3.8+ required, found $($matches[0])"
                return $false
            }
        } else {
            Write-Error "Could not determine Python version"
            return $false
        }
    } catch {
        Write-Error "Python not found. Please install Python 3.8+ first."
        Write-Info "Download from: https://www.python.org/downloads/"
        return $false
    }
}

function Install-PythonDependencies {
    Write-Info "Installing Python dependencies..."
    
    try {
        # Install pip dependencies
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        
        # Install Windows-specific dependencies
        python -m pip install pywin32 wmi
        
        Write-Success "Python dependencies installed successfully"
        return $true
    } catch {
        Write-Error "Failed to install Python dependencies: $_"
        return $false
    }
}

function Create-InstallationDirectories {
    Write-Info "Creating installation directories..."
    
    try {
        # Create main installation directory
        if (-not (Test-Path $InstallPath)) {
            New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        }
        
        # Create data directory
        $dataPath = "C:\ProgramData\MasterDashboard"
        if (-not (Test-Path $dataPath)) {
            New-Item -ItemType Directory -Path $dataPath -Force | Out-Null
        }
        
        # Create logs directory
        $logsPath = "$dataPath\logs"
        if (-not (Test-Path $logsPath)) {
            New-Item -ItemType Directory -Path $logsPath -Force | Out-Null
        }
        
        Write-Success "Installation directories created"
        return $true
    } catch {
        Write-Error "Failed to create directories: $_"
        return $false
    }
}

function Copy-AgentFiles {
    Write-Info "Copying agent files..."
    
    try {
        # Copy Python files
        Copy-Item "agent.py" -Destination $InstallPath -Force
        Copy-Item "requirements.txt" -Destination $InstallPath -Force
        
        # Copy shared modules if they exist
        $sharedPath = "..\shared"
        if (Test-Path $sharedPath) {
            $sharedDestPath = "$InstallPath\shared"
            if (-not (Test-Path $sharedDestPath)) {
                New-Item -ItemType Directory -Path $sharedDestPath -Force | Out-Null
            }
            Copy-Item "$sharedPath\*" -Destination $sharedDestPath -Recurse -Force
        }
        
        Write-Success "Agent files copied successfully"
        return $true
    } catch {
        Write-Error "Failed to copy agent files: $_"
        return $false
    }
}

function Create-Configuration {
    Write-Info "Creating configuration file..."
    
    try {
        $configPath = "$InstallPath\config.json"
        
        # Load base configuration
        $config = Get-Content "config.json" | ConvertFrom-Json
        
        # Update server URL if provided
        if ($ServerUrl -ne "http://localhost:8000") {
            $config.server.url = $ServerUrl
        }
        
        # Update paths for Windows
        $config.logging.file = "C:\ProgramData\MasterDashboard\logs\agent.log"
        
        # Prompt for server URL if not provided and not unattended
        if (-not $Unattended -and $config.server.url -eq "http://localhost:8000") {
            $userServerUrl = Read-Host "Enter Master Dashboard server URL (default: http://localhost:8000)"
            if ($userServerUrl) {
                $config.server.url = $userServerUrl
            }
        }
        
        # Save configuration
        $config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
        
        Write-Success "Configuration file created: $configPath"
        return $true
    } catch {
        Write-Error "Failed to create configuration: $_"
        return $false
    }
}

function Install-WindowsService {
    Write-Info "Installing Windows service..."
    
    try {
        # Change to installation directory
        Push-Location $InstallPath
        
        # Install the service
        python agent.py install
        
        # Set service to start automatically
        Set-Service -Name $ServiceName -StartupType Automatic
        
        Pop-Location
        
        Write-Success "Windows service installed successfully"
        return $true
    } catch {
        Write-Error "Failed to install Windows service: $_"
        Pop-Location
        return $false
    }
}

function Test-Installation {
    Write-Info "Testing installation..."
    
    try {
        Push-Location $InstallPath
        
        # Test connection to server
        $testResult = python agent.py test
        
        Pop-Location
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Installation test passed"
            return $true
        } else {
            Write-Warning "Installation test failed - server may not be accessible"
            return $false
        }
    } catch {
        Write-Warning "Could not test installation: $_"
        Pop-Location
        return $false
    }
}

function Start-AgentService {
    Write-Info "Starting Master Dashboard Agent service..."
    
    try {
        Start-Service -Name $ServiceName
        
        # Wait a moment and check if service is running
        Start-Sleep -Seconds 3
        $service = Get-Service -Name $ServiceName
        
        if ($service.Status -eq "Running") {
            Write-Success "Service started successfully"
            return $true
        } else {
            Write-Error "Service failed to start"
            return $false
        }
    } catch {
        Write-Error "Failed to start service: $_"
        return $false
    }
}

# Main installation process
try {
    Write-Info "Starting Master Dashboard Agent installation..."
    Write-Info "Installation Path: $InstallPath"
    Write-Info "Server URL: $ServerUrl"
    Write-Host ""
    
    # Check prerequisites
    if (-not (Test-PythonInstallation)) {
        exit 1
    }
    
    # Create directories
    if (-not (Create-InstallationDirectories)) {
        exit 1
    }
    
    # Copy files
    if (-not (Copy-AgentFiles)) {
        exit 1
    }
    
    # Install dependencies
    Push-Location $InstallPath
    if (-not (Install-PythonDependencies)) {
        Pop-Location
        exit 1
    }
    Pop-Location
    
    # Create configuration
    if (-not (Create-Configuration)) {
        exit 1
    }
    
    # Install Windows service
    if (-not (Install-WindowsService)) {
        exit 1
    }
    
    # Test installation
    $testPassed = Test-Installation
    
    # Start service
    if (-not (Start-AgentService)) {
        Write-Warning "Service installation completed but failed to start"
        Write-Info "You can start it manually with: Start-Service $ServiceName"
    }
    
    Write-Host ""
    Write-Success "🎉 Master Dashboard Agent installation completed!"
    Write-Host ""
    Write-Host "Service Information:" -ForegroundColor Cyan
    Write-Host "  Name: $ServiceName"
    Write-Host "  Installation: $InstallPath"
    Write-Host "  Configuration: $InstallPath\config.json"
    Write-Host "  Logs: C:\ProgramData\MasterDashboard\logs\"
    Write-Host ""
    Write-Host "Useful Commands:" -ForegroundColor Cyan
    Write-Host "  Start service:    Start-Service $ServiceName"
    Write-Host "  Stop service:     Stop-Service $ServiceName"
    Write-Host "  Restart service:  Restart-Service $ServiceName"
    Write-Host "  Check status:     Get-Service $ServiceName"
    Write-Host "  Test connection:  cd '$InstallPath'; python agent.py test"
    Write-Host "  Uninstall:        .\uninstall.ps1"
    Write-Host ""
    
    if (-not $testPassed) {
        Write-Warning "Note: Connection test failed. Please check your server URL and network connectivity."
    }
    
} catch {
    Write-Error "Installation failed: $_"
    exit 1
}