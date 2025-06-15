@echo off
REM Master Dashboard Agent Installation Script for Windows
REM This script installs the agent as a Windows service

setlocal EnableDelayedExpansion

REM Configuration
set "AGENT_NAME=MasterDashboardAgent"
set "SERVICE_NAME=MasterDashboardAgent"
set "INSTALL_DIR=%ProgramFiles%\MasterDashboardAgent"
set "CONFIG_DIR=%ProgramData%\MasterDashboardAgent"
set "LOG_DIR=%CONFIG_DIR%\logs"
set "PYTHON_MIN_VERSION=3.8"

REM Get script directory
set "SCRIPT_DIR=%~dp0"
for %%i in ("%SCRIPT_DIR%..") do set "CLIENT_DIR=%%~fi"

echo Master Dashboard Agent Installation Script
echo ==========================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click on the script and select "Run as administrator"
    pause
    exit /b 1
)

REM Check Python installation
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
echo [SUCCESS] Python %PYTHON_VERSION% detected

REM Create directories
echo [INFO] Creating directories...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
echo [SUCCESS] Directories created

REM Install dependencies
echo [INFO] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r "%CLIENT_DIR%\requirements.txt"
if %errorLevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed

REM Copy files
echo [INFO] Copying agent files...
xcopy "%CLIENT_DIR%\*.py" "%INSTALL_DIR%\" /Y /Q >nul 2>&1
xcopy "%CLIENT_DIR%\collectors" "%INSTALL_DIR%\collectors\" /E /I /Y /Q >nul 2>&1
xcopy "%CLIENT_DIR%\communication" "%INSTALL_DIR%\communication\" /E /I /Y /Q >nul 2>&1
xcopy "%CLIENT_DIR%\utils" "%INSTALL_DIR%\utils\" /E /I /Y /Q >nul 2>&1
xcopy "%CLIENT_DIR%\windows" "%INSTALL_DIR%\windows\" /E /I /Y /Q >nul 2>&1

REM Copy configuration
if exist "%CLIENT_DIR%\config.yaml" (
    copy "%CLIENT_DIR%\config.yaml" "%CONFIG_DIR%\config.yaml" >nul
)

echo [SUCCESS] Files copied

REM Configure agent
echo [INFO] Configuring agent...
set /p "SERVER_URL=Enter Master Dashboard server URL [http://localhost:8000]: "
if "%SERVER_URL%"=="" set "SERVER_URL=http://localhost:8000"

set /p "API_KEY=Enter API key: "
if "%API_KEY%"=="" (
    echo ERROR: API key is required
    pause
    exit /b 1
)

REM Update configuration using Python
python -c "
import yaml
import os

config_file = r'%CONFIG_DIR%\config.yaml'
try:
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    config = {}

# Update configuration
config.setdefault('server', {})
config['server']['url'] = '%SERVER_URL%'
config['server']['websocket_url'] = '%SERVER_URL%'.replace('http', 'ws') + '/ws'

config.setdefault('authentication', {})
config['authentication']['api_key'] = '%API_KEY%'

config.setdefault('logging', {})
config['logging']['file'] = r'%LOG_DIR%\agent.log'

with open(config_file, 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print('Configuration updated')
"

echo [SUCCESS] Configuration completed

REM Install Windows service
echo [INFO] Installing Windows service...
python "%INSTALL_DIR%\windows\service.py" install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install Windows service
    pause
    exit /b 1
)
echo [SUCCESS] Windows service installed

REM Start service
echo [INFO] Starting agent service...
sc start "%SERVICE_NAME%" >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Failed to start service automatically
    echo You can start it manually from Services or run: sc start %SERVICE_NAME%
) else (
    echo [SUCCESS] Agent service started successfully
)

REM Show completion message
echo.
echo [SUCCESS] Master Dashboard Agent installation completed!
echo.
echo Service name: %SERVICE_NAME%
echo Installation directory: %INSTALL_DIR%
echo Configuration file: %CONFIG_DIR%\config.yaml
echo Log directory: %LOG_DIR%
echo.
echo Useful commands:
echo   Status:  sc query %SERVICE_NAME%
echo   Start:   sc start %SERVICE_NAME%
echo   Stop:    sc stop %SERVICE_NAME%
echo   Restart: sc stop %SERVICE_NAME% ^&^& sc start %SERVICE_NAME%
echo   Remove:  sc delete %SERVICE_NAME%
echo.
echo You can also manage the service through Windows Services (services.msc^)
echo.
pause