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

from database.routes import crosswalk as crosswalk

# Ensure backend directory (this file's directory) is on sys.path for bare imports
_BACKEND_DIR = os.path.dirname(__file__)
if _BACKEND_DIR not in sys.path:  # idempotent
    sys.path.insert(0, _BACKEND_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.duckdb_cxn import engine
from database.models import Base
from database.routes import profiles, exports, datamodel, snowflake_export
from database.routes import auto_mapping

# Create FastAPI app
app = FastAPI(
    title="Crosswalk Aarete - Agentic Data Engineering Tool",
    description="Data engineering tool for column mapping and validation. Created by Diana Valladares.",
    version="1.0.0"
)

# CORS middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
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

# Serve static files from the frontend
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
async def _print_routes():
    print("\n=== ROUTES ===")
    for r in app.router.routes:
        try:
            print(r.path, getattr(r, "methods", None))
        except Exception:
            pass
    print("==============\n")