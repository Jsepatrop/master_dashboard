#!/bin/bash

# Master Dashboard Linux Agent Installation Script
# This script installs the Master Dashboard Agent on Linux systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_URL="http://localhost:8000"
INSTALL_DIR="/opt/master-dashboard-agent"
SERVICE_NAME="master-dashboard-agent"
USER_NAME="dashboard"
LOG_DIR="/var/log"
DATA_DIR="/var/lib/master-dashboard"

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

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python 3.8+
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    python_major=$(echo $python_version | cut -d'.' -f1)
    python_minor=$(echo $python_version | cut -d'.' -f2)
    
    if [[ $python_major -lt 3 ]] || [[ $python_major -eq 3 && $python_minor -lt 8 ]]; then
        log_error "Python 3.8+ required, found $python_version"
        exit 1
    fi
    
    log_success "Python $python_version found"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_warning "pip3 not found, installing..."
        if command -v apt-get &> /dev/null; then
            apt-get update && apt-get install -y python3-pip
        elif command -v yum &> /dev/null; then
            yum install -y python3-pip
        elif command -v dnf &> /dev/null; then
            dnf install -y python3-pip
        elif command -v pacman &> /dev/null; then
            pacman -S --noconfirm python-pip
        else
            log_error "Could not install pip3. Please install manually."
            exit 1
        fi
    fi
    
    # Check systemd
    if ! command -v systemctl &> /dev/null; then
        log_error "systemd is required but not found. This installer supports systemd-based distributions only."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

create_user() {
    log_info "Creating system user..."
    
    if ! id "$USER_NAME" &> /dev/null; then
        useradd --system --no-create-home --shell /bin/false "$USER_NAME"
        log_success "Created system user: $USER_NAME"
    else
        log_info "User $USER_NAME already exists"
    fi
}

create_directories() {
    log_info "Creating directories..."
    
    # Installation directory
    mkdir -p "$INSTALL_DIR"
    chown "$USER_NAME:$USER_NAME" "$INSTALL_DIR"
    chmod 755 "$INSTALL_DIR"
    
    # Data directory
    mkdir -p "$DATA_DIR"
    chown "$USER_NAME:$USER_NAME" "$DATA_DIR"
    chmod 755 "$DATA_DIR"
    
    # Log directory (agent will write here)
    touch "$LOG_DIR/master-dashboard-agent.log"
    chown "$USER_NAME:$USER_NAME" "$LOG_DIR/master-dashboard-agent.log"
    chmod 644 "$LOG_DIR/master-dashboard-agent.log"
    
    log_success "Directories created"
}

install_agent_files() {
    log_info "Installing agent files..."
    
    # Copy agent files
    cp agent.py "$INSTALL_DIR/"
    cp requirements.txt "$INSTALL_DIR/"
    
    # Copy shared modules
    if [[ -d "../shared" ]]; then
        cp -r ../shared "$INSTALL_DIR/"
    fi
    
    # Set permissions
    chown -R "$USER_NAME:$USER_NAME" "$INSTALL_DIR"
    chmod +x "$INSTALL_DIR/agent.py"
    
    log_success "Agent files installed"
}

setup_python_environment() {
    log_info "Setting up Python virtual environment..."
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    chown -R "$USER_NAME:$USER_NAME" venv
    
    # Install dependencies
    sudo -u "$USER_NAME" venv/bin/pip install --upgrade pip
    sudo -u "$USER_NAME" venv/bin/pip install -r requirements.txt
    
    log_success "Python environment set up"
}

configure_agent() {
    log_info "Configuring agent..."
    
    # Create configuration file
    if [[ ! -f "$INSTALL_DIR/config.json" ]]; then
        cp config.json "$INSTALL_DIR/config.json"
        
        # Prompt for server URL if not set
        if [[ "$SERVER_URL" == "http://localhost:8000" ]] && [[ "$1" != "--unattended" ]]; then
            echo
            read -p "Enter Master Dashboard server URL (default: http://localhost:8000): " input_url
            if [[ -n "$input_url" ]]; then
                SERVER_URL="$input_url"
            fi
        fi
        
        # Update configuration with server URL
        sed -i "s|http://localhost:8000|$SERVER_URL|g" "$INSTALL_DIR/config.json"
        
        # Update log file path
        sed -i "s|/var/log/master-dashboard-agent.log|$LOG_DIR/master-dashboard-agent.log|g" "$INSTALL_DIR/config.json"
        
        chown "$USER_NAME:$USER_NAME" "$INSTALL_DIR/config.json"
        chmod 640 "$INSTALL_DIR/config.json"
        
        log_success "Configuration created"
    else
        log_info "Configuration file already exists"
    fi
}

install_systemd_service() {
    log_info "Installing systemd service..."
    
    # Copy and update service file
    cp master-dashboard-agent.service /etc/systemd/system/
    
    # Update service file with actual paths and user
    sed -i "s|User=dashboard|User=$USER_NAME|g" /etc/systemd/system/master-dashboard-agent.service
    sed -i "s|Group=dashboard|Group=$USER_NAME|g" /etc/systemd/system/master-dashboard-agent.service
    sed -i "s|/opt/master-dashboard-agent|$INSTALL_DIR|g" /etc/systemd/system/master-dashboard-agent.service
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable master-dashboard-agent
    
    log_success "Systemd service installed and enabled"
}

test_installation() {
    log_info "Testing installation..."
    
    cd "$INSTALL_DIR"
    
    # Test configuration
    if sudo -u "$USER_NAME" venv/bin/python agent.py test; then
        log_success "Installation test passed"
        return 0
    else
        log_warning "Installation test failed - server may not be accessible"
        return 1
    fi
}

start_service() {
    log_info "Starting Master Dashboard Agent service..."
    
    systemctl start master-dashboard-agent
    sleep 3
    
    if systemctl is-active --quiet master-dashboard-agent; then
        log_success "Service started successfully"
        return 0
    else
        log_error "Service failed to start"
        return 1
    fi
}

show_status() {
    echo
    log_info "Service status:"
    systemctl status master-dashboard-agent --no-pager -l
}

show_completion_info() {
    echo
    log_success "🎉 Master Dashboard Agent installation completed!"
    echo
    echo "Service Information:"
    echo "  Name: $SERVICE_NAME"
    echo "  Installation: $INSTALL_DIR"
    echo "  Configuration: $INSTALL_DIR/config.json"
    echo "  Logs: $LOG_DIR/master-dashboard-agent.log"
    echo "  User: $USER_NAME"
    echo
    echo "Useful Commands:"
    echo "  Start service:    sudo systemctl start master-dashboard-agent"
    echo "  Stop service:     sudo systemctl stop master-dashboard-agent"
    echo "  Restart service:  sudo systemctl restart master-dashboard-agent"
    echo "  Check status:     sudo systemctl status master-dashboard-agent"
    echo "  View logs:        sudo journalctl -u master-dashboard-agent -f"
    echo "  Test connection:  cd $INSTALL_DIR && sudo -u $USER_NAME venv/bin/python agent.py test"
    echo "  Uninstall:        sudo ./uninstall.sh"
    echo
}

# Parse command line arguments
UNATTENDED=false
SKIP_START=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --server-url)
            SERVER_URL="$2"
            shift 2
            ;;
        --unattended)
            UNATTENDED=true
            shift
            ;;
        --skip-start)
            SKIP_START=true
            shift
            ;;
        --help|-h)
            echo "Master Dashboard Linux Agent Installation Script"
            echo
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Options:"
            echo "  --server-url URL    Set server URL (default: http://localhost:8000)"
            echo "  --unattended        Run in unattended mode (no prompts)"
            echo "  --skip-start        Install but don't start the service"
            echo "  --help, -h          Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Main installation process
echo "==========================================="
echo "  Master Dashboard Agent Installation"
echo "==========================================="
echo

log_info "Starting installation..."
log_info "Server URL: $SERVER_URL"
log_info "Installation Directory: $INSTALL_DIR"
echo

# Check if we're running as root
check_root

# Run installation steps
check_prerequisites
create_user
create_directories
install_agent_files
setup_python_environment
configure_agent $([[ $UNATTENDED == true ]] && echo "--unattended")
install_systemd_service

# Test installation
test_passed=true
if ! test_installation; then
    test_passed=false
fi

# Start service unless skipped
if [[ $SKIP_START == false ]]; then
    if ! start_service; then
        log_warning "Service installation completed but failed to start"
        log_info "You can start it manually with: sudo systemctl start master-dashboard-agent"
        show_status
    fi
else
    log_info "Service installation completed (start skipped)"
fi

# Show completion information
show_completion_info

if [[ $test_passed == false ]]; then
    log_warning "Note: Connection test failed. Please check your server URL and network connectivity."
fi

log_success "Installation completed successfully!"