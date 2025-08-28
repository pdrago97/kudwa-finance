# 🐳 Kudwa Financial AI System - Docker Setup

The simplest way to run the complete Kudwa Financial AI System with LangExtract integration.

## 🚀 Quick Start (3 Steps)

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- OpenAI API key
- Supabase account (free tier works)

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

**Required settings in `.env`:**
```bash
# OpenAI API Key (required for LangExtract)
OPENAI_API_KEY=sk-your-openai-api-key

# Supabase Database (required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### 3. Run
```bash
# Automated setup
./docker-setup.sh

# OR manual setup
docker-compose up -d
```

## 🌐 Access Points

Once running, access:
- **Dashboard**: http://localhost:8000/dashboard
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 Management Commands

```bash
# View logs
docker-compose logs -f

# Stop system
docker-compose down

# Restart
docker-compose restart

# Rebuild after code changes
docker-compose build && docker-compose up -d
```

## 🔧 Advanced Configuration

### Using Local Database
```bash
# Start with local PostgreSQL
docker-compose --profile local-db up -d
```

### With Redis Caching
```bash
# Start with Redis cache
docker-compose --profile cache up -d
```

### All Services
```bash
# Start everything
docker-compose --profile local-db --profile cache up -d
```

## 🐛 Troubleshooting

### Application Won't Start
```bash
# Check logs
docker-compose logs kudwa-app

# Common issues:
# 1. Missing API keys in .env
# 2. Invalid Supabase credentials
# 3. Port 8000 already in use
```

### LangExtract Issues
```bash
# Verify OpenAI API key is set
docker-compose exec kudwa-app env | grep OPENAI

# Test LangExtract manually
docker-compose exec kudwa-app python -c "import langextract; print('LangExtract OK')"
```

### Database Connection Issues
```bash
# Test Supabase connection
docker-compose exec kudwa-app python -c "
from supabase import create_client
import os
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
print('Supabase OK')
"
```

## 📦 What's Included

- **Kudwa Financial AI System** (main application)
- **LangExtract Integration** (document processing)
- **Dashboard Interface** (web UI)
- **REST API** (programmatic access)
- **Health Monitoring** (system status)

## 🔄 Development Workflow

1. **Make changes** to code
2. **Rebuild**: `docker-compose build`
3. **Restart**: `docker-compose up -d`
4. **Test**: Visit http://localhost:8000/dashboard

## 📚 Next Steps

1. **Upload Documents**: Use the File Upload section
2. **Review Entities**: Check the Approvals section
3. **Approve Items**: Build your knowledge graph
4. **Explore Data**: View ontology classes and relationships

## 🆘 Support

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify your `.env` configuration
3. Ensure Docker has sufficient resources (4GB+ RAM recommended)
4. Check that ports 8000 is available
