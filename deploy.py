#!/usr/bin/env python3
"""
Deployment script for the Interactive Crosswalk & ETL Helper
Serves both the FastAPI backend and the built frontend
"""

import os
import sys
import uvicorn

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app

if __name__ == "__main__":
    # Ensure the frontend is built
    frontend_dist_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")
    if not os.path.exists(frontend_dist_path):
        print("❌ Frontend not built. Please run 'cd frontend && npm run build' first.")
        exit(1)
    
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