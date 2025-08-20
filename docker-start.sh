#!/bin/bash

# Simple Docker Compose startup script
echo "🏦 Starting Kudwa Platform with Docker Compose..."

# Stop existing containers and start fresh
echo "🛑 Stopping existing containers..."
sudo docker-compose down

echo "🔨 Building and starting all services..."
sudo docker-compose up --build

# This will run in foreground and show logs
# Use Ctrl+C to stop all services
