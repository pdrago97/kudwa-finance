# Kudwa Local Startup Guide

## Quick Start

Start the entire Kudwa system with one command:

```bash
./start_kudwa.sh
```

This will automatically:
- ✅ Check prerequisites (Python 3.8+)
- ✅ Setup virtual environment
- ✅ Install dependencies
- ✅ Start all services:
  - **FastAPI Backend** (port 8000)
  - **Chat Dashboard** (port 8051)
  - **Mock N8N Webhook** (port 8052)

## Available Commands

```bash
# Start all services (default)
./start_kudwa.sh start

# Stop all services
./start_kudwa.sh stop

# Check service status
./start_kudwa.sh status

# View logs for a specific service
./start_kudwa.sh logs fastapi
./start_kudwa.sh logs dashboard
./start_kudwa.sh logs mock_webhook
```

## Service URLs

Once started, access these URLs:

- **🧠 Chat Dashboard**: http://localhost:8051
  - Main ontology extension interface
  - Upload documents and chat with AI agent
  - Human-in-the-loop validation buttons

- **📚 API Documentation**: http://localhost:8000/api/v1/docs
  - FastAPI interactive documentation
  - Test API endpoints directly

- **🔧 Mock Webhook**: http://localhost:8052
  - Local testing webhook that mimics N8N responses
  - Returns structured JSON responses for testing

## Testing

Run the test suite to verify everything is working:

```bash
python test_kudwa_services.py
```

## Configuration

### Using Mock Webhooks (Recommended for Development)

Add to your `.env` file:
```bash
USE_MOCK_WEBHOOK=true
```

This will route all webhook calls to the local mock server instead of the real N8N instance.

### Environment Variables

Key variables in `.env`:
- `N8N_ONTOLOGY_WEBHOOK` - Real N8N webhook URL
- `N8N_X_API_KEY` - API key for N8N authentication
- `USE_MOCK_WEBHOOK` - Set to 'true' for local testing
- `SUPABASE_URL` - Supabase project URL
- `OPENAI_API_KEY` - OpenAI API key

## Troubleshooting

### Services Won't Start
- Check Python version: `python3 --version` (needs 3.8+)
- Verify ports are free: `lsof -i :8000 -i :8051 -i :8052`
- Check logs: `tail -f logs/*.log`

### Dependencies Issues
- Delete virtual environment: `rm -rf venv`
- Run startup script again: `./start_kudwa.sh`

### Dashboard Not Loading
- Check if port 8051 is accessible
- Verify dashboard logs: `./start_kudwa.sh logs dashboard`
- Try refreshing browser

## Development Workflow

1. **Start services**: `./start_kudwa.sh`
2. **Open dashboard**: http://localhost:8051
3. **Test with mock data**: Upload a document or send a chat message
4. **View structured responses**: The dashboard will show ontology extensions and data proposals
5. **Use validation buttons**: Accept/reject proposals to test the full workflow

## File Structure

```
Kudwa/
├── start_kudwa.sh              # Main startup script
├── test_kudwa_services.py      # Service test suite
├── isolated_chat_dashboard.py  # Dashboard application
├── mock_n8n_webhook.py         # Mock webhook server
├── app/                        # FastAPI backend
├── logs/                       # Service logs
├── pids/                       # Process ID files
└── requirements-minimal.txt    # Essential dependencies
```

## Next Steps

- **Production**: Update `.env` with real N8N webhook URLs
- **Scaling**: Use Docker containers for deployment
- **Monitoring**: Add health checks and alerting
- **Security**: Configure proper authentication and HTTPS
