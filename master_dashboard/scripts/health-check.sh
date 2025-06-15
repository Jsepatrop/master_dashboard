#!/bin/bash

# Master Dashboard Health Check Script
# Comprehensive health monitoring for all system components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
NGINX_URL="http://localhost"
TIMEOUT=10
RETRIES=3

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_service() {
    local service_name="$1"
    local url="$2"
    local expected_status="$3"
    
    log_info "Checking $service_name..."
    
    local attempts=0
    while [[ $attempts -lt $RETRIES ]]; do
        if curl -f -s --max-time $TIMEOUT "$url" > /dev/null 2>&1; then
            log_success "$service_name is healthy"
            return 0
        fi
        
        attempts=$((attempts + 1))
        if [[ $attempts -lt $RETRIES ]]; then
            log_warning "$service_name check failed, retrying... ($attempts/$RETRIES)"
            sleep 2
        fi
    done
    
    log_error "$service_name is not responding after $RETRIES attempts"
    return 1
}

check_docker_services() {
    log_info "Checking Docker services status..."
    
    if command -v docker-compose &> /dev/null; then
        local services=$(docker-compose ps --services)
        local running_services=$(docker-compose ps --services --filter status=running)
    else
        local services=$(docker compose ps --services)
        local running_services=$(docker compose ps --services --filter status=running)
    fi
    
    for service in $services; do
        if echo "$running_services" | grep -q "^$service$"; then
            log_success "Docker service '$service' is running"
        else
            log_error "Docker service '$service' is not running"
        fi
    done
}

check_api_endpoints() {
    log_info "Checking API endpoints..."
    
    # Health endpoint
    if curl -f -s --max-time $TIMEOUT "$BACKEND_URL/api/v1/health" | grep -q "healthy\|ok"; then
        log_success "Health endpoint is working"
    else
        log_error "Health endpoint is not working"
    fi
    
    # Machines endpoint
    if curl -f -s --max-time $TIMEOUT "$BACKEND_URL/api/v1/machines" > /dev/null 2>&1; then
        log_success "Machines API endpoint is working"
    else
        log_error "Machines API endpoint is not working"
    fi
    
    # Metrics endpoint
    if curl -f -s --max-time $TIMEOUT "$BACKEND_URL/api/v1/metrics/latest" > /dev/null 2>&1; then
        log_success "Metrics API endpoint is working"
    else
        log_error "Metrics API endpoint is not working"
    fi
    
    # Alerts endpoint
    if curl -f -s --max-time $TIMEOUT "$BACKEND_URL/api/v1/alerts/active" > /dev/null 2>&1; then
        log_success "Alerts API endpoint is working"
    else
        log_error "Alerts API endpoint is not working"
    fi
}

check_websocket_connection() {
    log_info "Checking WebSocket connection..."
    
    # Try to connect to WebSocket endpoint
    if command -v wscat &> /dev/null; then
        if timeout 5 wscat -c "ws://localhost:8000/ws/data" --execute 'exit' &> /dev/null; then
            log_success "WebSocket connection is working"
        else
            log_error "WebSocket connection failed"
        fi
    else
        log_warning "wscat not installed, skipping WebSocket test"
    fi
}

check_resource_usage() {
    log_info "Checking resource usage..."
    
    # Check Docker container resource usage
    if command -v docker &> /dev/null; then
        local containers=$(docker ps --format "table {{.Names}}\t{{.CPUPerc}}\t{{.MemUsage}}" --filter "name=master-dashboard" 2>/dev/null || true)
        
        if [[ -n "$containers" ]]; then
            echo "Container Resource Usage:"
            echo "$containers"
        else
            log_warning "No Master Dashboard containers found"
        fi
    fi
    
    # Check system resources
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')
    local disk_usage=$(df / | tail -1 | awk '{printf "%s", $5}')
    
    log_info "System Memory Usage: $memory_usage"
    log_info "System Disk Usage: $disk_usage"
}

check_logs_for_errors() {
    log_info "Checking recent logs for errors..."
    
    if command -v docker-compose &> /dev/null; then
        local error_count=$(docker-compose logs --tail=100 2>/dev/null | grep -i "error\|exception\|failed" | wc -l || echo "0")
    else
        local error_count=$(docker compose logs --tail=100 2>/dev/null | grep -i "error\|exception\|failed" | wc -l || echo "0")
    fi
    
    if [[ $error_count -gt 0 ]]; then
        log_warning "Found $error_count error/exception entries in recent logs"
    else
        log_success "No errors found in recent logs"
    fi
}

generate_health_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="health-report-$(date '+%Y%m%d-%H%M%S').txt"
    
    log_info "Generating health report: $report_file"
    
    {
        echo "Master Dashboard Health Report"
        echo "Generated: $timestamp"
        echo "=============================="
        echo
        
        echo "Service Status:"
        check_service "Backend API" "$BACKEND_URL/api/v1/health" "200" 2>&1
        check_service "Frontend" "$FRONTEND_URL" "200" 2>&1
        check_service "Nginx Proxy" "$NGINX_URL/health" "200" 2>&1
        echo
        
        echo "Docker Services:"
        check_docker_services 2>&1
        echo
        
        echo "Resource Usage:"
        check_resource_usage 2>&1
        echo
        
        echo "Recent Errors:"
        check_logs_for_errors 2>&1
        
    } > "$report_file"
    
    log_success "Health report saved to $report_file"
}

run_comprehensive_check() {
    echo "========================================"
    echo "  Master Dashboard Health Check"
    echo "========================================"
    echo
    
    local overall_status=0
    
    # Check core services
    check_service "Backend API" "$BACKEND_URL/api/v1/health" "200" || overall_status=1
    check_service "Frontend" "$FRONTEND_URL" "200" || overall_status=1
    
    echo
    
    # Check Docker services
    check_docker_services || overall_status=1
    
    echo
    
    # Check API endpoints
    check_api_endpoints || overall_status=1
    
    echo
    
    # Check WebSocket
    check_websocket_connection || overall_status=1
    
    echo
    
    # Check resources
    check_resource_usage
    
    echo
    
    # Check logs
    check_logs_for_errors
    
    echo
    echo "========================================"
    
    if [[ $overall_status -eq 0 ]]; then
        log_success "🎉 All health checks passed! Master Dashboard is healthy."
        echo
        echo "Access URLs:"
        echo "  • Frontend: $FRONTEND_URL"
        echo "  • Backend:  $BACKEND_URL"
        echo "  • API Docs: $BACKEND_URL/docs"
    else
        log_error "❌ Some health checks failed. Please review the issues above."
        echo
        echo "Troubleshooting:"
        echo "  • Check service logs: docker-compose logs"
        echo "  • Restart services: docker-compose restart"
        echo "  • Redeploy: ./scripts/deploy.sh"
    fi
    
    return $overall_status
}

# Handle command line arguments
case "${1:-}" in
    "--report")
        generate_health_report
        ;;
    "--services-only")
        check_docker_services
        ;;
    "--api-only")
        check_api_endpoints
        ;;
    "--resources-only")
        check_resource_usage
        ;;
    "--help" | "-h")
        echo "Master Dashboard Health Check Script"
        echo
        echo "Usage: $0 [OPTION]"
        echo
        echo "Options:"
        echo "  --report         Generate detailed health report"
        echo "  --services-only  Check Docker services only"
        echo "  --api-only       Check API endpoints only"
        echo "  --resources-only Check resource usage only"
        echo "  --help, -h       Show this help message"
        echo
        echo "Without options, runs comprehensive health check."
        ;;
    "")
        run_comprehensive_check
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information."
        exit 1
        ;;
esac
