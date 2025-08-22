"""
FastAPI application for the Interactive Crosswalk & ETL Helper.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from database import engine
from models import Base
from routes import profiles, exports, datamodel
from routes import crosswalk_new as crosswalk

# Create FastAPI app
app = FastAPI(
    title="Interactive Crosswalk & ETL Helper",
    description="Data engineering tool for column mapping and validation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(profiles.router, prefix="/api")
app.include_router(crosswalk.router, prefix="/api")
app.include_router(exports.router, prefix="/api")
app.include_router(datamodel.router)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "crosswalk-etl-helper"}

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    Base.metadata.create_all(bind=engine)
