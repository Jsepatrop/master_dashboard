@echo off
REM Master Dashboard Agent Uninstallation Script for Windows
REM This script removes the agent and all its components

setlocal EnableDelayedExpansion

REM Configuration
set "AGENT_NAME=MasterDashboardAgent"
set "SERVICE_NAME=MasterDashboardAgent"
set "INSTALL_DIR=%ProgramFiles%\MasterDashboardAgent"
set "CONFIG_DIR=%ProgramData%\MasterDashboardAgent"

echo Master Dashboard Agent Uninstallation
echo =====================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click on the script and select "Run as administrator"
    pause
    exit /b 1
)

echo WARNING: This will completely remove the Master Dashboard Agent from your system.
echo The following will be removed:
echo   - Service: %SERVICE_NAME%
echo   - Installation directory: %INSTALL_DIR%
echo   - Configuration directory: %CONFIG_DIR%
echo.

set /p "CONFIRM=Are you sure you want to continue? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo [INFO] Uninstallation cancelled
    pause
    exit /b 0
)

echo.
echo [INFO] Starting uninstallation...

REM Stop service
echo [INFO] Stopping agent service...
sc query "%SERVICE_NAME%" >nul 2>&1
if %errorLevel% equ 0 (
    sc stop "%SERVICE_NAME%" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [SUCCESS] Service stopped
        REM Wait for service to stop
        timeout /t 3 >nul
    ) else (
        echo [WARNING] Failed to stop service or service already stopped
    )
) else (
    echo [INFO] Service is not installed
)

REM Remove service
echo [INFO] Removing Windows service...
sc query "%SERVICE_NAME%" >nul 2>&1
if %errorLevel% equ 0 (
    sc delete "%SERVICE_NAME%" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [SUCCESS] Service removed
    ) else (
        echo [ERROR] Failed to remove service
    )
) else (
    echo [INFO] Service is not installed
)

REM Remove installation directory
echo [INFO] Removing installation directory...
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [SUCCESS] Installation directory removed: %INSTALL_DIR%
    ) else (
        echo [ERROR] Failed to remove installation directory
        echo Some files may be in use. Try rebooting and running this script again.
    )
) else (
    echo [INFO] Installation directory not found: %INSTALL_DIR%
)

REM Ask about configuration directory
set /p "REMOVE_CONFIG=Remove configuration directory? (%CONFIG_DIR%) [y/N]: "
if /i "%REMOVE_CONFIG%"=="y" (
    if exist "%CONFIG_DIR%" (
        rmdir /s /q "%CONFIG_DIR%" >nul 2>&1
        if %errorLevel% equ 0 (
            echo [SUCCESS] Configuration directory removed: %CONFIG_DIR%
        ) else (
            echo [ERROR] Failed to remove configuration directory
        )
    ) else (
        echo [INFO] Configuration directory not found: %CONFIG_DIR%
    )
) else (
    echo [INFO] Configuration directory preserved: %CONFIG_DIR%
)

REM Ask about Python packages
echo.
set /p "REMOVE_PACKAGES=Remove Python packages installed for the agent? [y/N]: "
if /i "%REMOVE_PACKAGES%"=="y" (
    echo [WARNING] This might affect other Python applications
    set /p "CONFIRM_PACKAGES=Continue? [y/N]: "
    if /i "!CONFIRM_PACKAGES!"=="y" (
        echo [INFO] Removing Python packages...
        python -m pip uninstall -y psutil pynvml py-cpuinfo distro websockets aiohttp pyyaml cryptography netifaces colorlog click rich pywin32 wmi >nul 2>&1
        echo [SUCCESS] Python packages removed
    )
)

REM Show completion message
echo.
echo [SUCCESS] Master Dashboard Agent uninstallation completed!
echo.

if exist "%CONFIG_DIR%" (
    echo [INFO] Configuration directory preserved: %CONFIG_DIR%
    echo You can manually remove this directory if no longer needed
    echo.
)

echo Press any key to exit...
pause >nul