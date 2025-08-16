#!/bin/bash

# Kudwa CrewAI System Stop Script
# This script stops all Kudwa system services

echo "🛑 Stopping Kudwa CrewAI Financial System..."
echo "============================================="

# Function to kill process by PID file
kill_by_pidfile() {
    local pidfile=$1
    local service_name=$2
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔄 Stopping $service_name (PID: $pid)..."
            kill -TERM "$pid" 2>/dev/null
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚡ Force killing $service_name..."
                kill -9 "$pid" 2>/dev/null
            fi
            echo "✅ $service_name stopped"
        else
            echo "ℹ️  $service_name was not running"
        fi
        rm -f "$pidfile"
    else
        echo "ℹ️  No PID file found for $service_name"
    fi
}

# Kill services by PID files
kill_by_pidfile ".fastapi.pid" "FastAPI Server"
kill_by_pidfile ".dashboard.pid" "Dashboard"

# Kill any remaining processes on our ports
echo "🧹 Cleaning up any remaining processes..."

# Kill processes on port 8000 (FastAPI)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "🔄 Killing remaining processes on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

# Kill processes on port 8051 (Dashboard)
if lsof -Pi :8051 -sTCP:LISTEN -t >/dev/null ; then
    echo "🔄 Killing remaining processes on port 8051..."
    lsof -ti:8051 | xargs kill -9 2>/dev/null || true
fi

echo ""
echo "✅ All Kudwa services have been stopped"
echo "📝 Log files are preserved in the logs/ directory"
echo ""
