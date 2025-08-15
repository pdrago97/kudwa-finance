#!/bin/bash

# Kudwa AI Financial System - Complete Local Startup Script
# This script starts all components of the Kudwa system locally

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
PID_DIR="$PROJECT_DIR/pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ❌ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}"
    echo "=============================================================="
    echo "🧠 Kudwa AI Financial System - Local Startup"
    echo "=============================================================="
    echo -e "${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process by PID file
kill_by_pidfile() {
    local pidfile=$1
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            print_status "Stopping process with PID $pid"
            kill "$pid"
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                print_warning "Force killing process $pid"
                kill -9 "$pid"
            fi
        fi
        rm -f "$pidfile"
    fi
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up processes..."
    kill_by_pidfile "$PID_DIR/fastapi.pid"
    kill_by_pidfile "$PID_DIR/dashboard.pid"
    kill_by_pidfile "$PID_DIR/mock_webhook.pid"
    
    # Kill any remaining processes on our ports
    for port in 8000 8051 8052; do
        if check_port $port; then
            print_status "Killing process on port $port"
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done
    
    print_success "Cleanup completed"
}

# Set trap for cleanup on script exit
trap cleanup EXIT INT TERM

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Python 3.8+ is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    python_major=$(echo $python_version | cut -d. -f1)
    python_minor=$(echo $python_version | cut -d. -f2)

    if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
        print_error "Python 3.8+ is required. Found: $python_version"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        print_error ".env file not found. Please create it from .env.example"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements - try minimal first, then full
    if [ -f "$PROJECT_DIR/requirements-minimal.txt" ]; then
        print_status "Installing minimal Python dependencies..."
        pip install -r "$PROJECT_DIR/requirements-minimal.txt"
    elif [ -f "$PROJECT_DIR/requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install -r "$PROJECT_DIR/requirements.txt"
    fi
    
    print_success "Virtual environment setup completed"
}

# Function to start FastAPI backend
start_fastapi() {
    print_status "Starting FastAPI backend on port 8000..."
    
    if check_port 8000; then
        print_warning "Port 8000 is already in use"
        return 1
    fi
    
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Start FastAPI in background
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$LOG_DIR/fastapi.log" 2>&1 &
    echo $! > "$PID_DIR/fastapi.pid"
    
    # Wait for service to start
    sleep 3
    if check_port 8000; then
        print_success "FastAPI backend started successfully"
        print_status "API Documentation: http://localhost:8000/api/v1/docs"
        return 0
    else
        print_error "Failed to start FastAPI backend"
        return 1
    fi
}

# Function to start isolated chat dashboard
start_dashboard() {
    print_status "Starting Isolated Chat Dashboard on port 8051..."
    
    if check_port 8051; then
        print_warning "Port 8051 is already in use"
        return 1
    fi
    
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Start dashboard in background
    nohup python start_isolated_dashboard.py > "$LOG_DIR/dashboard.log" 2>&1 &
    echo $! > "$PID_DIR/dashboard.pid"
    
    # Wait for service to start
    sleep 3
    if check_port 8051; then
        print_success "Isolated Chat Dashboard started successfully"
        print_status "Dashboard URL: http://localhost:8051"
        return 0
    else
        print_error "Failed to start dashboard"
        return 1
    fi
}

# Function to start mock N8N webhook (for testing)
start_mock_webhook() {
    print_status "Starting Mock N8N Webhook on port 8052..."
    
    if check_port 8052; then
        print_warning "Port 8052 is already in use"
        return 1
    fi
    
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Start mock webhook in background
    nohup python mock_n8n_webhook.py > "$LOG_DIR/mock_webhook.log" 2>&1 &
    echo $! > "$PID_DIR/mock_webhook.pid"
    
    # Wait for service to start
    sleep 2
    if check_port 8052; then
        print_success "Mock N8N Webhook started successfully"
        print_status "Mock Webhook URL: http://localhost:8052"
        return 0
    else
        print_warning "Mock webhook failed to start (optional component)"
        return 0
    fi
}

# Function to display running services
show_services() {
    echo -e "${CYAN}"
    echo "=============================================================="
    echo "🚀 Kudwa Services Status"
    echo "=============================================================="
    echo -e "${NC}"
    
    if check_port 8000; then
        print_success "FastAPI Backend: http://localhost:8000"
        print_status "  └─ API Docs: http://localhost:8000/api/v1/docs"
        print_status "  └─ Health Check: http://localhost:8000/health"
    else
        print_error "FastAPI Backend: Not running"
    fi
    
    if check_port 8051; then
        print_success "Chat Dashboard: http://localhost:8051"
        print_status "  └─ Ontology Extension Interface"
    else
        print_error "Chat Dashboard: Not running"
    fi
    
    if check_port 8052; then
        print_success "Mock N8N Webhook: http://localhost:8052"
        print_status "  └─ Testing endpoint for webhook integration"
    else
        print_warning "Mock N8N Webhook: Not running (optional)"
    fi
    
    echo -e "${CYAN}"
    echo "=============================================================="
    echo "📋 Useful Commands:"
    echo "  • View logs: tail -f logs/*.log"
    echo "  • Stop all: Ctrl+C or kill this script"
    echo "  • Check processes: ps aux | grep python"
    echo "=============================================================="
    echo -e "${NC}"
}

# Main execution
main() {
    print_header
    
    # Parse command line arguments
    case "${1:-start}" in
        "start")
            check_prerequisites
            setup_venv
            
            print_status "Starting all Kudwa services..."
            
            # Start services
            start_fastapi
            start_dashboard
            start_mock_webhook
            
            show_services
            
            print_success "All services started successfully!"
            print_status "Press Ctrl+C to stop all services"
            
            # Keep script running
            while true; do
                sleep 10
                # Check if services are still running
                if ! check_port 8000 && ! check_port 8051; then
                    print_error "All services have stopped"
                    break
                fi
            done
            ;;
        "stop")
            print_status "Stopping all services..."
            cleanup
            ;;
        "status")
            show_services
            ;;
        "logs")
            if [ -n "$2" ]; then
                tail -f "$LOG_DIR/$2.log"
            else
                print_status "Available logs: fastapi, dashboard, mock_webhook"
                print_status "Usage: $0 logs <service_name>"
            fi
            ;;
        *)
            echo "Usage: $0 {start|stop|status|logs [service_name]}"
            echo ""
            echo "Commands:"
            echo "  start  - Start all Kudwa services (default)"
            echo "  stop   - Stop all running services"
            echo "  status - Show status of all services"
            echo "  logs   - View logs for a specific service"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
