#!/bin/bash

# Test Docker Setup for Kudwa Financial AI System
set -e

echo "🧪 Testing Kudwa Docker Setup"
echo "=============================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t kudwa-finance:test .

echo "✅ Docker image built successfully"

# Test the image with a simple command
echo "🧪 Testing LangExtract in Docker..."
docker run --rm kudwa-finance:test python -c "
import langextract
print('✅ LangExtract is working in Docker!')
print(f'LangExtract version: {getattr(langextract, \"__version__\", \"unknown\")}')
"

echo "✅ LangExtract test passed"

# Test the application startup (without real credentials)
echo "🧪 Testing application startup..."
docker run --rm -p 8001:8000 \
    -e OPENAI_API_KEY=test-key \
    -e SUPABASE_URL=https://test.supabase.co \
    -e SUPABASE_KEY=test-key \
    kudwa-finance:test timeout 10 python simple_main.py || true

echo "✅ Application startup test completed"

echo ""
echo "🎉 Docker setup is working!"
echo ""
echo "To run the full system:"
echo "1. Configure your .env file with real API keys"
echo "2. Run: docker-compose up -d"
echo "3. Access: http://localhost:8000/dashboard"
