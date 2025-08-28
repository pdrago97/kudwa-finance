#!/bin/bash

# Kudwa Financial AI System - Docker Setup Script
# Simple approach to get everything running with Docker

set -e

echo "🚀 Kudwa Financial AI System - Docker Setup"
echo "============================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Please edit .env file with your API keys:"
    echo "   - OPENAI_API_KEY (required for LangExtract)"
    echo "   - SUPABASE_URL and SUPABASE_KEY (required for database)"
    echo ""
    echo "   Run: nano .env"
    echo ""
    read -p "Press Enter after you've configured your .env file..."
fi

# Validate required environment variables
echo "🔍 Validating configuration..."
source .env

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key" ]; then
    echo "❌ OPENAI_API_KEY is not configured in .env file"
    echo "   This is required for LangExtract to work"
    exit 1
fi

if [ -z "$SUPABASE_URL" ] || [ "$SUPABASE_URL" = "https://your-project.supabase.co" ]; then
    echo "❌ SUPABASE_URL is not configured in .env file"
    echo "   This is required for the database"
    exit 1
fi

if [ -z "$SUPABASE_KEY" ] || [ "$SUPABASE_KEY" = "your-anon-key" ]; then
    echo "❌ SUPABASE_KEY is not configured in .env file"
    echo "   This is required for the database"
    exit 1
fi

echo "✅ Configuration validated"

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting Kudwa Financial AI System..."
docker-compose up -d

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if the application is running
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Kudwa Financial AI System is running!"
    echo ""
    echo "🌐 Access the application:"
    echo "   Dashboard: http://localhost:8000/dashboard"
    echo "   API Docs:  http://localhost:8000/docs"
    echo "   Health:    http://localhost:8000/health"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:    docker-compose logs -f"
    echo "   Stop system:  docker-compose down"
    echo "   Restart:      docker-compose restart"
    echo ""
else
    echo "❌ Application failed to start. Check logs:"
    echo "   docker-compose logs"
fi
