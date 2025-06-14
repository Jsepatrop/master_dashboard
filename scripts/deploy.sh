#!/bin/bash

# Master Dashboard Deployment Script
# This script automates the deployment of the Master Dashboard system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="master-dashboard"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
HEALTH_CHECK_RETRIES=10
HEALTH_CHECK_DELAY=30

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

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if running as root (not recommended)
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root is not recommended for security reasons."
        read -p "Do you want to continue? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_success "Prerequisites check passed."
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f "$ENV_FILE" ]]; then
        if [[ -f ".env.example" ]]; then
            cp .env.example $ENV_FILE
            log_info "Created $ENV_FILE from .env.example"
            log_warning "Please review and update the environment variables in $ENV_FILE"
        else
            log_error ".env.example file not found. Cannot create environment file."
            exit 1
        fi
    fi
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data
    
    log_success "Environment setup completed."
}

build_services() {
    log_info "Building Docker services..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose build --no-cache
    else
        docker compose build --no-cache
    fi
    
    log_success "Docker services built successfully."
}

start_services() {
    log_info "Starting Master Dashboard services..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    log_success "Services started successfully."
}

wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    local retries=0
    while [[ $retries -lt $HEALTH_CHECK_RETRIES ]]; do
        if curl -f http://localhost:8000/api/v1/health &> /dev/null; then
            log_success "Backend service is ready."
            break
        fi
        
        retries=$((retries + 1))
        log_info "Waiting for backend service... (attempt $retries/$HEALTH_CHECK_RETRIES)"
        sleep $HEALTH_CHECK_DELAY
    done
    
    if [[ $retries -eq $HEALTH_CHECK_RETRIES ]]; then
        log_error "Backend service failed to start within the expected time."
        show_service_logs
        exit 1
    fi
    
    # Check frontend
    retries=0
    while [[ $retries -lt $HEALTH_CHECK_RETRIES ]]; do
        if curl -f http://localhost:3000 &> /dev/null; then
            log_success "Frontend service is ready."
            break
        fi
        
        retries=$((retries + 1))
        log_info "Waiting for frontend service... (attempt $retries/$HEALTH_CHECK_RETRIES)"
        sleep $HEALTH_CHECK_DELAY
    done
    
    if [[ $retries -eq $HEALTH_CHECK_RETRIES ]]; then
        log_error "Frontend service failed to start within the expected time."
        show_service_logs
        exit 1
    fi
}

show_service_status() {
    log_info "Checking service status..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
}

show_service_logs() {
    log_info "Recent service logs:"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose logs --tail=20
    else
        docker compose logs --tail=20
    fi
}

run_health_check() {
    log_info "Running comprehensive health check..."
    
    if [[ -f "scripts/health-check.sh" ]]; then
        bash scripts/health-check.sh
    else
        log_warning "Health check script not found. Performing basic checks..."
        
        # Basic health checks
        if curl -f http://localhost:8000/api/v1/health &> /dev/null; then
            log_success "✓ Backend API is healthy"
        else
            log_error "✗ Backend API is not responding"
        fi
        
        if curl -f http://localhost:3000 &> /dev/null; then
            log_success "✓ Frontend is healthy"
        else
            log_error "✗ Frontend is not responding"
        fi
    fi
}

show_deployment_info() {
    echo
    log_success "🎉 Master Dashboard deployment completed successfully!"
    echo
    echo "Access URLs:"
    echo "  • Frontend (Web Interface): http://localhost:3000"
    echo "  • Backend API:              http://localhost:8000"
    echo "  • API Documentation:        http://localhost:8000/docs"
    echo
    echo "Useful Commands:"
    echo "  • View logs:         docker-compose logs -f"
    echo "  • Stop services:     docker-compose down"
    echo "  • Restart services:  docker-compose restart"
    echo "  • Health check:      ./scripts/health-check.sh"
    echo
    log_info "For more information, check the README.md file."
}

cleanup_on_failure() {
    log_error "Deployment failed. Cleaning up..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    exit 1
}

# Trap for cleanup on failure
trap cleanup_on_failure ERR

# Main deployment flow
main() {
    echo "====================================="
    echo "  Master Dashboard Deployment"
    echo "====================================="
    echo
    
    check_prerequisites
    setup_environment
    build_services
    start_services
    wait_for_services
    show_service_status
    run_health_check
    show_deployment_info
}

# Handle command line arguments
case "${1:-}" in
    "--build-only")
        check_prerequisites
        setup_environment
        build_services
        ;;
    "--start-only")
        start_services
        wait_for_services
        show_service_status
        ;;
    "--health-check")
        run_health_check
        ;;
    "--status")
        show_service_status
        ;;
    "--logs")
        show_service_logs
        ;;
    "--help" | "-h")
        echo "Master Dashboard Deployment Script"
        echo
        echo "Usage: $0 [OPTION]"
        echo
        echo "Options:"
        echo "  --build-only     Build Docker images only"
        echo "  --start-only     Start services only (skip build)"
        echo "  --health-check   Run health check only"
        echo "  --status         Show service status"
        echo "  --logs           Show recent logs"
        echo "  --help, -h       Show this help message"
        echo
        echo "Without options, performs full deployment."
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information."
        exit 1
        ;;
esac