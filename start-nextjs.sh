#!/bin/bash

# Kudwa Next.js Platform Startup Script
echo "🏦 Starting Kudwa Next.js Financial Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if frontend/.env exists
if [ ! -f frontend/.env ]; then
    echo "⚠️  frontend/.env file not found. Creating from frontend/.env.example..."
    if [ -f frontend/.env.example ]; then
        cp frontend/.env.example frontend/.env
        echo "📝 Please edit frontend/.env file with your configuration."
    fi
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Function to check service health with retries
check_service() {
    local url=$1
    local name=$2
    local max_attempts=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $name is running on $url"
            return 0
        fi
        echo "⏳ Waiting for $name... (attempt $attempt/$max_attempts)"
        sleep 3
        ((attempt++))
    done

    echo "⚠️  $name health check failed after $max_attempts attempts"
    return 1
}

# Check service health
echo "🔍 Checking service health..."

check_service "http://localhost:8000/health" "Backend API"
check_service "http://localhost:3000/api/health" "Frontend"
check_service "http://localhost:8501" "Streamlit (Legacy)"

echo ""
echo "🎉 Kudwa Platform is ready!"
echo ""
echo "📱 Access the application:"
echo "   • 🚀 Next.js Frontend: http://localhost:3000"
echo "   • 🔧 Backend API: http://localhost:8000"
echo "   • 📚 API Docs: http://localhost:8000/docs"
echo "   • 📊 Streamlit (Legacy): http://localhost:8501"
echo ""
echo "🔧 Development commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • View specific service: docker-compose logs -f frontend"
echo "   • Stop services: docker-compose down"
echo "   • Restart service: docker-compose restart frontend"
echo ""
echo "🐛 Troubleshooting:"
echo "   • If frontend fails to start, check: docker-compose logs frontend"
echo "   • If backend fails, check: docker-compose logs backend"
echo "   • To rebuild: docker-compose down && docker-compose up --build"
echo ""

# Ask if user wants to follow logs
read -p "📋 Follow logs? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📋 Following logs (Ctrl+C to stop)..."
    docker-compose logs -f
else
    echo "✅ Platform is running in the background!"
    echo "💡 Use 'docker-compose logs -f' to view logs anytime"
fi
