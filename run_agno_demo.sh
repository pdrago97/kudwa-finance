#!/bin/bash

# Kudwa Finance - Agno Integration Demo Launcher
# This script launches the Streamlit demo for Agno integration

echo "🧠 Kudwa Finance - Agno Integration Demo"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# OpenAI API Key (required for Agno)
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic API Key (required for Agno)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Supabase Configuration
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Agno Configuration
AGNO_CLAUDE_MODEL=claude-sonnet-4-20250514
AGNO_OPENAI_MODEL=gpt-4o
AGNO_REASONING_ENABLED=true
AGNO_MULTI_MODAL=true
EOF
    echo "✅ Created .env template. Please add your API keys before running the demo."
    echo ""
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check API keys
echo "🔍 Checking configuration..."

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
    echo "⚠️  OpenAI API key not configured"
    MISSING_KEYS=true
fi

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your-anthropic-api-key-here" ]; then
    echo "⚠️  Anthropic API key not configured"
    MISSING_KEYS=true
fi

if [ "$MISSING_KEYS" = true ]; then
    echo ""
    echo "📝 To get the full Agno experience, please configure your API keys in .env file:"
    echo "   - OpenAI API Key: https://platform.openai.com/api-keys"
    echo "   - Anthropic API Key: https://console.anthropic.com/"
    echo ""
    echo "🎯 You can still run the demo to see the interface and mock functionality."
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ API keys configured"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."

python -c "
import sys
missing_packages = []

try:
    import streamlit
    print('✅ Streamlit installed')
except ImportError:
    missing_packages.append('streamlit')

try:
    import plotly
    print('✅ Plotly installed')
except ImportError:
    missing_packages.append('plotly')

try:
    import agno
    print('✅ Agno installed')
except ImportError:
    missing_packages.append('agno')

try:
    import pandas
    print('✅ Pandas installed')
except ImportError:
    missing_packages.append('pandas')

try:
    import numpy
    print('✅ Numpy installed')
except ImportError:
    missing_packages.append('numpy')

if missing_packages:
    print(f'❌ Missing packages: {missing_packages}')
    print('Installing missing packages...')
    import subprocess
    for package in missing_packages:
        subprocess.run([sys.executable, '-m', 'pip', 'install', package])
    print('✅ Dependencies installed')
else:
    print('✅ All dependencies satisfied')
"

echo ""
echo "🚀 Starting Streamlit Agno Demo..."
echo ""
echo "📱 The demo will open in your browser at: http://localhost:8501"
echo ""
echo "🎯 Demo Features:"
echo "   • 🏠 Overview - System architecture and features"
echo "   • 🧠 Reasoning Engine - Step-by-step financial analysis"
echo "   • 📄 Document Analysis - Upload and analyze financial documents"
echo "   • 🔗 Bridge System - Intelligent framework routing"
echo "   • 📊 Performance Comparison - Agno vs CrewAI metrics"
echo "   • 🎨 Interface Creator - AI-powered UI generation"
echo ""
echo "💡 Tips:"
echo "   • Use the sidebar to navigate between demo modes"
echo "   • Try uploading sample financial documents"
echo "   • Experiment with different reasoning scenarios"
echo "   • Check the performance comparisons"
echo ""
echo "🛑 To stop the demo, press Ctrl+C"
echo ""

# Launch Streamlit
streamlit run streamlit_agno_demo.py --server.port 8501 --server.address localhost

echo ""
echo "👋 Demo stopped. Thank you for trying Kudwa Finance - Agno Integration!"
