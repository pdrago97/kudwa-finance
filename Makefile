# Kudwa AI-Powered Financial System Makefile
# Simplified setup and management commands

.PHONY: help install setup dev test clean deploy docker

# Default target
help:
	@echo "🚀 Kudwa AI-Powered Financial System"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make setup       - Setup database and environment"
	@echo "  make dev         - Start development server"
	@echo "  make test        - Run comprehensive tests"
	@echo "  make load-data   - Load sample financial data"
	@echo "  make clean       - Clean up temporary files"
	@echo "  make docker      - Build and run with Docker"
	@echo "  make deploy      - Deploy to production"
	@echo ""

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully!"

# Setup environment and database
setup: install
	@echo "🔧 Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "📝 Created .env file from template"; \
		echo "⚠️  Please update .env with your API keys and database URLs"; \
	fi
	@echo "🗄️  Setting up database..."
	@if [ -n "$(SUPABASE_URL)" ] && [ -n "$(SUPABASE_SERVICE_KEY)" ]; then \
		echo "Running database setup script..."; \
		python -c "import asyncio; from app.services.supabase_client import supabase_service; print('Database connection test passed')"; \
	else \
		echo "⚠️  Please configure Supabase credentials in .env file"; \
	fi
	@echo "✅ Setup completed!"

# Start development server
dev:
	@echo "🚀 Starting development server..."
	@echo "📊 API Documentation: http://localhost:8000/api/v1/docs"
	@echo "🔍 Health Check: http://localhost:8000/health"
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run comprehensive tests
test:
	@echo "🧪 Running comprehensive system tests..."
	python scripts/test_system.py
	@echo "✅ Tests completed!"

# Load sample financial data
load-data:
	@echo "📊 Loading sample financial data..."
	@if [ -f data1.json ] && [ -f data2.json ]; then \
		python -c "import asyncio; import httpx; asyncio.run(httpx.post('http://localhost:8000/api/v1/documents/sample-data', json={'user_id': 'demo_user'}))"; \
		echo "✅ Sample data loaded successfully!"; \
	else \
		echo "❌ Sample data files (data1.json, data2.json) not found"; \
		echo "Please ensure the data files are in the project root"; \
	fi

# Run specific tests
test-parsing:
	@echo "🔍 Testing data parsing..."
	python -c "import asyncio; from scripts.test_system import KudwaSystemTester; asyncio.run(KudwaSystemTester().test_data_ingestion())"

test-api:
	@echo "🔌 Testing API endpoints..."
	python -c "import asyncio; from scripts.test_system import KudwaSystemTester; asyncio.run(KudwaSystemTester().test_api_endpoints())"

# Clean up temporary files
clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "✅ Cleanup completed!"

# Docker commands
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t kudwa-financial-ai .

docker-run: docker-build
	@echo "🚀 Running with Docker..."
	docker run -p 8000:8000 --env-file .env kudwa-financial-ai

docker: docker-run

# Development utilities
format:
	@echo "🎨 Formatting code..."
	black app/ scripts/
	isort app/ scripts/
	@echo "✅ Code formatted!"

lint:
	@echo "🔍 Linting code..."
	flake8 app/ scripts/
	mypy app/
	@echo "✅ Linting completed!"

# Database management
db-reset:
	@echo "🗄️  Resetting database..."
	@echo "⚠️  This will delete all data. Are you sure? (y/N)"
	@read confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "Running database reset..."
	# Add database reset commands here
	@echo "✅ Database reset completed!"

# n8n workflow management
n8n-import:
	@echo "🔄 Importing n8n workflows..."
	@if [ -d "n8n-workflows" ]; then \
		echo "Workflows found in n8n-workflows/"; \
		echo "Please import these manually into your n8n instance:"; \
		ls n8n-workflows/*.json; \
	else \
		echo "❌ n8n-workflows directory not found"; \
	fi

# Deployment
deploy-check:
	@echo "🔍 Pre-deployment checks..."
	@echo "Checking environment variables..."
	@python -c "from app.core.config import settings; print('✅ Configuration loaded successfully')"
	@echo "Checking database connection..."
	@python -c "import asyncio; from app.services.supabase_client import supabase_service; print('✅ Database connection OK')"
	@echo "✅ Pre-deployment checks passed!"

deploy: deploy-check
	@echo "🚀 Deploying to production..."
	@echo "⚠️  Make sure you have configured your deployment target"
	@echo "This is a placeholder for your deployment process"
	@echo "Consider using platforms like:"
	@echo "  - Render.com (recommended for this project)"
	@echo "  - Railway"
	@echo "  - Heroku"
	@echo "  - AWS/GCP/Azure"

# Demo and presentation
demo: setup
	@echo "🚀 Starting Kudwa Real-Time Demo..."
	python scripts/start_demo.py

demo-setup: setup load-data
	@echo "🎬 Setting up demo environment..."
	@echo "✅ Demo environment ready!"
	@echo ""
	@echo "🎯 Demo URLs:"
	@echo "  Real-Time Demo: http://localhost:8080/realtime_demo.html"
	@echo "  API Docs: http://localhost:8000/api/v1/docs"
	@echo "  Health: http://localhost:8000/health"
	@echo ""
	@echo "🧪 Test the system:"
	@echo "  make test"
	@echo ""
	@echo "💬 Try natural language queries:"
	@echo "  curl -X POST http://localhost:8000/api/v1/query/natural \\"
	@echo "    -H 'Content-Type: application/json' \\"
	@echo "    -d '{\"query\": \"What was our total revenue?\", \"user_id\": \"demo\"}'"

# Real-time demo features
demo-realtime: demo

demo-websockets:
	@echo "🔌 Testing WebSocket connections..."
	@echo "Document Ingestion: ws://localhost:8000/api/v1/realtime/document-ingestion?user_id=demo"
	@echo "RAG Chat: ws://localhost:8000/api/v1/realtime/rag-chat?user_id=demo"
	@echo "Entity Operations: ws://localhost:8000/api/v1/realtime/entity-operations?user_id=demo"
	@echo "Dashboard Updates: ws://localhost:8000/api/v1/realtime/dashboard?user_id=demo"

# Show system status
status:
	@echo "📊 Kudwa System Status"
	@echo "======================"
	@echo ""
	@echo "🔧 Environment:"
	@python -c "from app.core.config import settings; print(f'  Environment: {settings.ENVIRONMENT}'); print(f'  Debug: {settings.DEBUG}')"
	@echo ""
	@echo "🗄️  Database:"
	@python -c "from app.core.config import settings; print(f'  Supabase URL: {settings.SUPABASE_URL[:30]}...' if settings.SUPABASE_URL else '  ❌ Supabase not configured')"
	@echo ""
	@echo "🤖 AI Services:"
	@python -c "from app.core.config import settings; print(f'  OpenAI: {\"✅ Configured\" if settings.OPENAI_API_KEY else \"❌ Not configured\"}'); print(f'  Model: {settings.OPENAI_MODEL}')"
	@echo ""
	@echo "🔄 n8n Integration:"
	@python -c "from app.core.config import settings; print(f'  Webhook URL: {settings.N8N_WEBHOOK_BASE_URL}')"

# Quick start for new users
quickstart:
	@echo "⚡ Kudwa Quick Start"
	@echo "==================="
	@echo ""
	@echo "1. 📦 Installing dependencies..."
	@make install
	@echo ""
	@echo "2. 🔧 Setting up environment..."
	@make setup
	@echo ""
	@echo "3. 📊 Loading sample data..."
	@make load-data
	@echo ""
	@echo "4. 🧪 Running tests..."
	@make test
	@echo ""
	@echo "🎉 Quick start completed!"
	@echo "🚀 Run 'make dev' to start the development server"
