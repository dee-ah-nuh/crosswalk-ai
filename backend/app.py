"""FastAPI application for the Interactive Crosswalk & ETL Helper.

This module is designed to be importable both when the current working directory
is the backend folder (e.g. running ``uvicorn app:app`` from inside ``backend``)
and when running from the project root with ``uvicorn backend.app:app``.

Because many internal modules use bare imports like ``from database import ...``
we ensure the backend directory itself is added to ``sys.path`` when imported
as ``backend.app`` so those imports resolve without refactoring every module.
"""

import os
import sys

# Ensure backend directory (this file's directory) is on sys.path for bare imports
_BACKEND_DIR = os.path.dirname(__file__)
if _BACKEND_DIR not in sys.path:  # idempotent
    sys.path.insert(0, _BACKEND_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine
from models import Base
from routes import profiles, exports, datamodel, snowflake_export
from routes import crosswalk_new as crosswalk, auto_mapping

# Create FastAPI app
app = FastAPI(
    title="Interactive Crosswalk & ETL Helper",
    description="Data engineering tool for column mapping and validation",
    version="1.0.0"
)

# CORS middleware - allow all origins for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(profiles.router, prefix="/api")
app.include_router(crosswalk.router, prefix="/api")
app.include_router(exports.router, prefix="/api")
app.include_router(datamodel.router)
app.include_router(snowflake_export.router)
app.include_router(auto_mapping.router)

# Serve static files from the frontend build directory
frontend_dist_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(frontend_dist_path):
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="static")
else:
    print(f"⚠️  Warning: Frontend dist directory not found at {frontend_dist_path}")
    print("   Run 'cd frontend && npm run build' to build the frontend first.")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "crosswalk-etl-helper"}

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    Base.metadata.create_all(bind=engine)
