#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Kudwa POC Setup"
echo "=================="

# Check if .env exists
if [ ! -f .env ]; then
  echo "📝 No .env found. Copying .env.example to .env"
  cp .env.example .env
  echo "⚠️  Please fill in .env values (SUPABASE_URL, SUPABASE_SERVICE_KEY) and re-run if needed."
  echo ""
fi

# Check Docker installation
if ! command -v docker >/dev/null 2>&1; then
  echo "❌ Docker not found. Please install Docker first."
  exit 1
fi

# Detect docker compose vs docker-compose
if docker compose version >/dev/null 2>&1; then
  DOCKER_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  DOCKER_CMD="docker-compose"
else
  echo "❌ Neither 'docker compose' nor 'docker-compose' found."
  exit 1
fi

echo "🐳 Using: $DOCKER_CMD"
echo "🏗️  Building and starting services..."
echo ""

$DOCKER_CMD up --build

