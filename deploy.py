#!/usr/bin/env python3
"""
Deployment script for the Interactive Crosswalk & ETL Helper
Serves both the FastAPI backend and the built frontend
"""

import os
import sys
import subprocess
import uvicorn
from pathlib import Path

def build_frontend():
    """Build the frontend if not already built"""
    project_root = Path(__file__).parent
    frontend_path = project_root / "frontend"
    frontend_dist_path = frontend_path / "dist"
    
    if not frontend_dist_path.exists():
        print("🔨 Building frontend...")
        try:
            # Change to frontend directory and build
            original_cwd = os.getcwd()
            os.chdir(frontend_path)
            
            # Run npm build
            result = subprocess.run(["npm", "run", "build"], check=True, capture_output=True, text=True)
            print("✅ Frontend built successfully!")
            
            os.chdir(original_cwd)
        except subprocess.CalledProcessError as e:
            print(f"❌ Frontend build failed: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
            os.chdir(original_cwd)
            exit(1)
        except Exception as e:
            print(f"❌ Error building frontend: {e}")
            os.chdir(original_cwd)
            exit(1)
    else:
        print("✅ Frontend already built.")

def setup_backend():
    """Setup backend environment and imports"""
    # Add the backend directory to the Python path
    backend_path = Path(__file__).parent / 'backend'
    sys.path.insert(0, str(backend_path))
    
    # Set the working directory to backend for relative imports to work
    original_cwd = os.getcwd()
    os.chdir(backend_path)
    
    try:
        # Initialize database and seed data before importing app
        from database import init_db
        from seed_data import seed_initial_data
        
        # Initialize the database
        print("🔧 Initializing database...")
        init_db()
        print("🌱 Seeding initial data...")
        seed_initial_data()
        
        from app import app
        return app
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

if __name__ == "__main__":
    # Build the frontend first
    build_frontend()
    
    # Setup backend and get app instance
    app = setup_backend()
    
    print("🚀 Starting Interactive Crosswalk & ETL Helper...")
    print("📊 Backend API: http://0.0.0.0:5000/api/health")
    print("🌐 Frontend App: http://0.0.0.0:5000/")
    
    # Run the server on port 5000 for deployment
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        reload=False
    )