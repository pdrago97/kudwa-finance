# Docker Setup for Kudwa Platform

## Quick Start

### Option 1: Simple Docker Compose (Recommended)
```bash
sudo docker-compose down && sudo docker-compose up --build
```

### Option 2: Using the startup script
```bash
./docker-start.sh
```

### Option 3: Advanced startup with health checks
```bash
./start-nextjs.sh
```

## Services

The docker-compose.yml includes three services:

### 1. Frontend (Next.js) - Port 3000
- **URL**: http://localhost:3000
- **Health Check**: http://localhost:3000/api/health
- **Technology**: Next.js 14 with TypeScript
- **Features**: Modern UI, authentication, real-time updates

### 2. Backend (FastAPI) - Port 8000
- **URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Technology**: FastAPI with Supabase integration

### 3. Streamlit (Legacy) - Port 8501
- **URL**: http://localhost:8501
- **Technology**: Streamlit (for comparison/migration)

## Environment Configuration

### Frontend Environment
File: `frontend/.env`
```env
NEXT_PUBLIC_SUPABASE_URL=https://zafvnssmznpeurboybnd.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
NEXT_PUBLIC_BACKEND_URL=http://backend:8000
NODE_ENV=development
```

### Backend Environment
Configured directly in docker-compose.yml with your Supabase credentials.

## Docker Commands

### Start Services
```bash
# Start all services in background
sudo docker-compose up -d --build

# Start all services with logs
sudo docker-compose up --build

# Start specific service
sudo docker-compose up frontend --build
```

### View Logs
```bash
# All services
sudo docker-compose logs -f

# Specific service
sudo docker-compose logs -f frontend
sudo docker-compose logs -f backend
sudo docker-compose logs -f streamlit
```

### Stop Services
```bash
# Stop all services
sudo docker-compose down

# Stop and remove volumes
sudo docker-compose down -v
```

### Restart Services
```bash
# Restart specific service
sudo docker-compose restart frontend

# Restart all services
sudo docker-compose restart
```

## Troubleshooting

### Frontend Issues
```bash
# Check frontend logs
sudo docker-compose logs frontend

# Rebuild frontend only
sudo docker-compose up --build frontend

# Access frontend container
sudo docker-compose exec frontend sh
```

### Backend Issues
```bash
# Check backend logs
sudo docker-compose logs backend

# Test backend health
curl http://localhost:8000/health

# Access backend container
sudo docker-compose exec backend bash
```

### Network Issues
All services are on the `kudwa-network` bridge network for internal communication.

### Port Conflicts
If ports are already in use:
- Frontend: Change `3000:3000` to `3001:3000` in docker-compose.yml
- Backend: Change `8000:8000` to `8001:8000` in docker-compose.yml
- Streamlit: Change `8501:8501` to `8502:8501` in docker-compose.yml

## Development Workflow

1. **Start the platform**:
   ```bash
   sudo docker-compose up --build
   ```

2. **Make changes** to your code (auto-reload enabled)

3. **View logs** to debug:
   ```bash
   sudo docker-compose logs -f frontend
   ```

4. **Restart if needed**:
   ```bash
   sudo docker-compose restart frontend
   ```

5. **Stop when done**:
   ```bash
   sudo docker-compose down
   ```

## Production Notes

- The current setup is optimized for development
- For production, create a separate `docker-compose.prod.yml`
- Use environment variables for sensitive data
- Enable SSL/HTTPS for production deployment
- Consider using Docker Swarm or Kubernetes for scaling

## Next Steps

1. Access the Next.js frontend at http://localhost:3000
2. Create an account or login
3. Explore the modern dashboard
4. Compare with the legacy Streamlit interface at http://localhost:8501
5. Use the API documentation at http://localhost:8000/docs
