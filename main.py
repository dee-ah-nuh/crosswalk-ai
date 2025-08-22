#!/usr/bin/env python3
"""
Launcher script for the Interactive Crosswalk & ETL Helper application.
Starts both the FastAPI backend and serves the React frontend.
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def run_backend():
    """Run the FastAPI backend server"""
    try:
        import uvicorn
        from backend.app import app
        
        # Initialize database and seed data
        from backend.database import init_db
        from backend.seed_data import seed_initial_data
        
        init_db()
        seed_initial_data()
        
        # Start FastAPI server
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"Error starting backend: {e}")
        sys.exit(1)

def run_frontend():
    """Build and serve the React frontend"""
    try:
        frontend_dir = Path(__file__).parent / "frontend"
        os.chdir(frontend_dir)
        
        # Install dependencies if needed (handled separately)
        # Build the frontend
        subprocess.run(["npm", "run", "build"], check=True)
        
        # Serve the built frontend
        subprocess.run(["npx", "serve", "-s", "dist", "-l", "5000"], check=True)
    except Exception as e:
        print(f"Error starting frontend: {e}")
        sys.exit(1)

def main():
    """Main launcher function"""
    print("🚀 Starting Interactive Crosswalk & ETL Helper...")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(3)
    
    # Start frontend (this will block)
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down application...")
        sys.exit(0)

if __name__ == "__main__":
    main()
