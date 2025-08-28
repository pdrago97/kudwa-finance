# Kudwa Financial AI System - Complete Docker Setup with LangExtract
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements-docker.txt .

# Install Python dependencies with verbose output
RUN pip install --no-cache-dir --verbose -r requirements-docker.txt

# Verify LangExtract installation
RUN python -c "import langextract; print('✅ LangExtract successfully installed in Docker')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data uploads

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "simple_main.py"]
