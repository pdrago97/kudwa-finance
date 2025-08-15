#!/bin/bash

# Kudwa CrewAI System Startup Script
# This script starts all necessary services for the Kudwa financial AI system

echo "🚀 Starting Kudwa CrewAI Financial System..."
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your API keys."
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $port is already in use. Killing existing processes..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
check_port 8000
check_port 8051

# Start FastAPI server in background
echo "🔧 Starting FastAPI server on port 8000..."
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/fastapi.log 2>&1 &
FASTAPI_PID=$!

# Wait for FastAPI to start
echo "⏳ Waiting for FastAPI server to start..."
sleep 5

# Check if FastAPI is running
if curl -s http://localhost:8000/api/v1/crew/health > /dev/null; then
    echo "✅ FastAPI server started successfully"
else
    echo "❌ FastAPI server failed to start. Check logs/fastapi.log"
    exit 1
fi

# Start Dashboard in background
echo "📊 Starting CrewAI Dashboard on port 8051..."
nohup python crew_ai_dashboard.py > logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!

# Wait for Dashboard to start
echo "⏳ Waiting for Dashboard to start..."
sleep 3

# Check if Dashboard is running
if curl -s http://localhost:8051 > /dev/null; then
    echo "✅ Dashboard started successfully"
else
    echo "❌ Dashboard failed to start. Check logs/dashboard.log"
fi

echo ""
echo "🎉 Kudwa CrewAI System is now running!"
echo "=============================================="
echo "📍 Access Points:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • CrewAI Dashboard:   http://localhost:8051"
echo "   • API Health Check:   http://localhost:8000/api/v1/crew/health"
echo ""
echo "📋 Process IDs:"
echo "   • FastAPI Server: $FASTAPI_PID"
echo "   • Dashboard:      $DASHBOARD_PID"
echo ""
echo "📝 Logs:"
echo "   • FastAPI: logs/fastapi.log"
echo "   • Dashboard: logs/dashboard.log"
echo ""
echo "🛑 To stop all services, run: ./stop_kudwa_system.sh"
echo ""

# Save PIDs for stopping later
echo "$FASTAPI_PID" > .fastapi.pid
echo "$DASHBOARD_PID" > .dashboard.pid

# Run system test
echo "🧪 Running system health check..."
python test_system.py

echo ""
echo "✨ System startup complete! Happy analyzing! 🚀"
