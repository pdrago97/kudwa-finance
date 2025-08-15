#!/usr/bin/env python3
"""
Startup script for the CrewAI-powered Kudwa system
"""

import os
import sys
import subprocess
import time
import signal
import asyncio
from pathlib import Path
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

class CrewAISystemManager:
    """Manager for starting and stopping the CrewAI system"""
    
    def __init__(self):
        self.processes = {}
        self.base_dir = Path(__file__).parent
        
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        logger.info("Checking dependencies...")
        
        required_packages = [
            'crewai',
            'sentence-transformers',
            'faiss-cpu',
            'networkx',
            'pyvis',
            'fastapi',
            'supabase'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                logger.info(f"✅ {package} is installed")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"❌ {package} is missing")
        
        if missing_packages:
            logger.error("Missing dependencies", packages=missing_packages)
            print("\n🚨 Missing dependencies detected!")
            print("Please install them using:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        logger.info("✅ All dependencies are installed")
        return True
    
    def check_environment(self):
        """Check environment variables"""
        logger.info("Checking environment variables...")
        
        required_env_vars = [
            'OPENAI_API_KEY',
            'SUPABASE_URL',
            'SUPABASE_SERVICE_KEY'
        ]
        
        missing_vars = []
        
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                logger.warning(f"❌ {var} is not set")
            else:
                logger.info(f"✅ {var} is set")
        
        if missing_vars:
            logger.error("Missing environment variables", variables=missing_vars)
            print("\n🚨 Missing environment variables!")
            print("Please set the following variables in your .env file:")
            for var in missing_vars:
                print(f"  {var}=your_value_here")
            return False
        
        logger.info("✅ All environment variables are set")
        return True
    
    def initialize_vector_index(self):
        """Initialize the vector index for RAG operations"""
        logger.info("Initializing vector index...")
        
        try:
            # Import and initialize RAG manager
            from agents.rag_graph_manager import RAGGraphManager
            
            async def init_rag():
                rag_manager = RAGGraphManager()
                await rag_manager.initialize_vector_index()
                return rag_manager
            
            # Run async initialization
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            rag_manager = loop.run_until_complete(init_rag())
            loop.close()
            
            logger.info("✅ Vector index initialized successfully")
            return True
            
        except Exception as e:
            logger.error("Failed to initialize vector index", error=str(e))
            print(f"\n⚠️  Warning: Vector index initialization failed: {str(e)}")
            print("The system will still work, but semantic search may be limited.")
            return False
    
    def start_fastapi_server(self):
        """Start the FastAPI server"""
        logger.info("Starting FastAPI server...")
        
        try:
            cmd = [
                sys.executable, "-m", "uvicorn",
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes['fastapi'] = process
            logger.info("✅ FastAPI server started", pid=process.pid)
            
            # Wait a moment for server to start
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error("Failed to start FastAPI server", error=str(e))
            return False
    
    def start_crew_dashboard(self):
        """Start the CrewAI dashboard"""
        logger.info("Starting CrewAI dashboard...")
        
        try:
            cmd = [sys.executable, "crew_ai_dashboard.py"]
            
            process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes['dashboard'] = process
            logger.info("✅ CrewAI dashboard started", pid=process.pid)
            
            return True
            
        except Exception as e:
            logger.error("Failed to start CrewAI dashboard", error=str(e))
            return False
    
    def check_services_health(self):
        """Check if all services are running properly"""
        logger.info("Checking services health...")
        
        import requests
        import time
        
        # Check FastAPI server
        for attempt in range(5):
            try:
                response = requests.get("http://localhost:8000/api/v1/crew/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ FastAPI server is healthy")
                    break
            except requests.exceptions.RequestException:
                if attempt < 4:
                    logger.info(f"Waiting for FastAPI server... (attempt {attempt + 1}/5)")
                    time.sleep(2)
                else:
                    logger.warning("❌ FastAPI server health check failed")
                    return False
        
        # Check dashboard
        for attempt in range(3):
            try:
                response = requests.get("http://localhost:8051", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ CrewAI dashboard is healthy")
                    break
            except requests.exceptions.RequestException:
                if attempt < 2:
                    logger.info(f"Waiting for dashboard... (attempt {attempt + 1}/3)")
                    time.sleep(2)
                else:
                    logger.warning("❌ Dashboard health check failed")
                    return False
        
        return True
    
    def start_system(self):
        """Start the complete CrewAI system"""
        print("🚀 Starting Kudwa CrewAI System...")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Check environment
        if not self.check_environment():
            return False
        
        # Initialize vector index
        self.initialize_vector_index()
        
        # Start FastAPI server
        if not self.start_fastapi_server():
            return False
        
        # Start dashboard
        if not self.start_crew_dashboard():
            return False
        
        # Check health
        if not self.check_services_health():
            logger.warning("Some services may not be fully healthy")
        
        print("\n🎉 Kudwa CrewAI System Started Successfully!")
        print("=" * 50)
        print("📊 Dashboard: http://localhost:8051")
        print("🔗 API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("🤖 CrewAI Chat: http://localhost:8000/api/v1/crew/chat")
        print("\nPress Ctrl+C to stop the system")
        
        return True
    
    def stop_system(self):
        """Stop all system processes"""
        logger.info("Stopping CrewAI system...")
        
        for name, process in self.processes.items():
            try:
                logger.info(f"Stopping {name}...", pid=process.pid)
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {name}...")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping {name}", error=str(e))
        
        print("\n👋 Kudwa CrewAI System stopped")
    
    def run(self):
        """Run the system with signal handling"""
        def signal_handler(signum, frame):
            print("\n\n🛑 Shutdown signal received...")
            self.stop_system()
            sys.exit(0)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start system
        if self.start_system():
            try:
                # Keep the main process alive
                while True:
                    time.sleep(1)
                    
                    # Check if processes are still running
                    for name, process in list(self.processes.items()):
                        if process.poll() is not None:
                            logger.error(f"{name} process died", return_code=process.returncode)
                            # Optionally restart the process here
                            
            except KeyboardInterrupt:
                pass
            finally:
                self.stop_system()
        else:
            print("\n❌ Failed to start the system")
            sys.exit(1)


def main():
    """Main entry point"""
    manager = CrewAISystemManager()
    manager.run()


if __name__ == "__main__":
    main()
