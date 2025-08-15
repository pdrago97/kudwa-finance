#!/bin/bash

# Kudwa CrewAI System Startup Script
# This script starts the complete CrewAI-powered financial data processing system

set -e

echo "🚀 Kudwa CrewAI System Startup"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# Optional: Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
EOF
    echo "📝 Please edit .env file with your API keys and run this script again"
    exit 1
fi

# Load environment variables
echo "🔑 Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)

# Check if required environment variables are set
required_vars=("OPENAI_API_KEY" "SUPABASE_URL" "SUPABASE_SERVICE_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "your_${var,,}_here" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing or incomplete environment variables:"
    printf '   %s\n' "${missing_vars[@]}"
    echo "Please update your .env file with the correct values"
    exit 1
fi

# Install/upgrade dependencies
echo "📦 Installing/upgrading dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if all CrewAI dependencies are installed
echo "🔍 Checking CrewAI dependencies..."
python -c "
import sys
try:
    import crewai
    import sentence_transformers
    import faiss
    import networkx
    import pyvis
    print('✅ All CrewAI dependencies are installed')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "Installing missing CrewAI dependencies..."
    pip install crewai crewai-tools sentence-transformers faiss-cpu networkx pyvis neo4j
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p static
mkdir -p pids

# Start the CrewAI system
echo "🎯 Starting CrewAI system..."
python start_crew_ai_system.py

echo "👋 CrewAI system stopped"
