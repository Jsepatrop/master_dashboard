#!/bin/bash

# Master Dashboard Linux Agent Uninstall Script
# This script completely removes the Master Dashboard Agent from Linux systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/master-dashboard-agent"
SERVICE_NAME="master-dashboard-agent"
USER_NAME="dashboard"
LOG_FILE="/var/log/master-dashboard-agent.log"
DATA_DIR="/var/lib/master-dashboard"

# Command line options
KEEP_LOGS=false
KEEP_CONFIG=false
FORCE=false

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root. Use sudo."
        exit 1
    fi
}

confirm_uninstall() {
    if [[ $FORCE == true ]]; then
        return 0
    fi
    
    echo
    log_warning "This will completely remove the Master Dashboard Agent from this system."
    echo "Installation Directory: $INSTALL_DIR"
    echo "Service: $SERVICE_NAME"
    echo "User: $USER_NAME"
    echo "Data Directory: $DATA_DIR"
    echo "Log File: $LOG_FILE"
    
    if [[ $KEEP_LOGS == true ]]; then
        echo "Log files will be preserved."
    fi
    
    if [[ $KEEP_CONFIG == true ]]; then
        echo "Configuration files will be preserved."
    fi
    
    echo
    read -p "Are you sure you want to continue? (y/N) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Uninstall cancelled."
        exit 0
    fi
}

stop_service() {
    log_info "Stopping Master Dashboard Agent service..."
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        systemctl stop $SERVICE_NAME
        log_success "Service stopped"
    else
        log_info "Service was not running"
    fi
}

disable_service() {
    log_info "Disabling service..."
    
    if systemctl is-enabled --quiet $SERVICE_NAME 2>/dev/null; then
        systemctl disable $SERVICE_NAME
        log_success "Service disabled"
    else
        log_info "Service was not enabled"
    fi
}

remove_systemd_service() {
    log_info "Removing systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
    
    if [[ -f $SERVICE_FILE ]]; then
        rm -f $SERVICE_FILE
        systemctl daemon-reload
        log_success "Systemd service removed"
    else
        log_info "Systemd service file not found"
    fi
}

remove_installation_files() {
    log_info "Removing installation files..."
    
    if [[ -d $INSTALL_DIR ]]; then
        if [[ $KEEP_CONFIG == true ]]; then
            # Preserve config file
            if [[ -f "$INSTALL_DIR/config.json" ]]; then
                cp "$INSTALL_DIR/config.json" "/tmp/master-dashboard-config.json.backup"
                log_info "Configuration backed up to /tmp/master-dashboard-config.json.backup"
            fi
        fi
        
        rm -rf $INSTALL_DIR
        log_success "Installation files removed"
    else
        log_info "Installation directory not found"
    fi
}

remove_data_files() {
    log_info "Removing data files..."
    
    if [[ -d $DATA_DIR ]]; then
        rm -rf $DATA_DIR
        log_success "Data files removed"
    else
        log_info "Data directory not found"
    fi
}

remove_log_files() {
    if [[ $KEEP_LOGS == true ]]; then
        log_info "Preserving log files"
        return
    fi
    
    log_info "Removing log files..."
    
    if [[ -f $LOG_FILE ]]; then
        rm -f $LOG_FILE
        log_success "Log files removed"
    else
        log_info "Log file not found"
    fi
    
    # Remove rotated logs
    rm -f $LOG_FILE.*
}

remove_user() {
    log_info "Removing system user..."
    
    if id "$USER_NAME" &> /dev/null; then
        userdel "$USER_NAME" 2>/dev/null || true
        log_success "System user removed"
    else
        log_info "System user not found"
    fi
}

cleanup_remaining_files() {
    log_info "Cleaning up remaining files..."
    
    # Remove any remaining service files
    find /etc/systemd/system -name "*master-dashboard*" -delete 2>/dev/null || true
    
    # Remove any PID files
    rm -f /var/run/master-dashboard-agent.pid 2>/dev/null || true
    
    # Remove any temporary files
    rm -f /tmp/*master-dashboard* 2>/dev/null || true
    
    log_success "Cleanup completed"
}

show_completion_info() {
    echo
    log_success "🎉 Master Dashboard Agent uninstallation completed!"
    echo
    
    if [[ $KEEP_LOGS == true ]]; then
        log_info "Log files have been preserved at: $LOG_FILE"
    fi
    
    if [[ $KEEP_CONFIG == true ]] && [[ -f "/tmp/master-dashboard-config.json.backup" ]]; then
        log_info "Configuration backup saved at: /tmp/master-dashboard-config.json.backup"
    fi
    
    echo
    log_info "Thank you for using Master Dashboard Agent."
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --keep-logs)
            KEEP_LOGS=true
            shift
            ;;
        --keep-config)
            KEEP_CONFIG=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help|-h)
            echo "Master Dashboard Linux Agent Uninstall Script"
            echo
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Options:"
            echo "  --keep-logs     Preserve log files"
            echo "  --keep-config   Preserve configuration files"
            echo "  --force         Skip confirmation prompt"
            echo "  --help, -h      Show this help message"
            echo
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Main uninstallation process
echo "============================================="
echo "  Master Dashboard Agent Uninstallation"
echo "============================================="
echo

# Check if we're running as root
check_root

# Confirm uninstallation
confirm_uninstall

echo
log_info "Starting uninstallation..."

# Run uninstallation steps
stop_service || true
disable_service || true
remove_systemd_service || true
remove_installation_files || true
remove_data_files || true
remove_log_files || true
remove_user || true
cleanup_remaining_files || true

# Show completion information
show_completion_info

log_success "Uninstallation completed successfully!"