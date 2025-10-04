"""
FastAPI routes for profile management.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json

from database.duckdb_cxn import DuckDBClient
# and use DuckDBClient.get_duckdb as your dependency
from database.models import SourceProfile, SourceColumn, DataModelField

from services.file_parser import FileParser

router = APIRouter()

@router.post("/profiles")


@router.post("/profiles")
async def create_profile(
    name: str = Form(...),
    client_id: str = Form(""),
    db: Session = Depends(DuckDBClient.get_duckdb)
):
    """Create a new source profile"""
    logging.info(f"Received profile creation request: name={name}, client_id={client_id}")
    try:
        profile = SourceProfile(
            name=name,
            client_id=client_id if client_id else None
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        logging.info(f"Profile created: id={profile.id}, name={profile.name}, client_id={profile.client_id}")
        return {"id": profile.id, "name": profile.name, "client_id": profile.client_id}
    except Exception as e:
        logging.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating profile: {e}")

@router.get("/profiles")
async def list_profiles(db: Session = Depends(DuckDBClient.get_duckdb)):
    """List all profiles"""
    profiles = db.query(SourceProfile).all()
    return [{
        "id": p.id,
        "name": p.name,
        "client_id": p.client_id,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "has_physical_file": p.has_physical_file,
        "raw_table_name": p.raw_table_name
    } for p in profiles]

@router.get("/profiles/{profile_id}")
async def get_profile(profile_id: int, db: Session = Depends(DuckDBClient.get_duckdb)):
    """Get a specific profile"""
    profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "id": profile.id,
        "name": profile.name,
        "client_id": profile.client_id,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "has_physical_file": profile.has_physical_file,
        "raw_table_name": profile.raw_table_name
    }

@router.post("/profiles/{profile_id}/source/ingest-file")
async def ingest_file(
    profile_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(DuckDBClient.get_duckdb)
):
    """Upload and parse a source file (CSV/XLSX)"""
    profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse file
        column_names, column_data = FileParser.parse_file(file_content, file.filename)
        
        # Clear existing source columns
        db.query(SourceColumn).filter(SourceColumn.profile_id == profile_id).delete()
        
        # Create source columns
        for col_name in column_names:
            col_info = column_data.get(col_name, {})
            source_column = SourceColumn(
                profile_id=profile_id,
                source_column=col_name,
                sample_values_json=json.dumps(col_info.get('sample_values', [])),
                inferred_type=col_info.get('inferred_type', 'string')
            )
            db.add(source_column)
        
        # Update profile
        profile.has_physical_file = True
        
        db.commit()
        
        return {
            "message": "File ingested successfully",
            "columns_count": len(column_names),
            "columns": column_names
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/profiles/{profile_id}/source/ingest-schema")
async def ingest_schema(
    profile_id: int,
    schema_data: Dict[str, List[str]],
    db: Session = Depends(DuckDBClient.get_duckdb)
):
    """Ingest schema from column list"""
    profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    try:
        column_names = schema_data.get("columns", [])
        
        if not column_names:
            raise ValueError("No columns provided")
        
        # Clear existing source columns
        db.query(SourceColumn).filter(SourceColumn.profile_id == profile_id).delete()
        
        # Create source columns (without sample data)
        for col_name in column_names:
            source_column = SourceColumn(
                profile_id=profile_id,
                source_column=col_name.strip(),
                sample_values_json=json.dumps([]),
                inferred_type='string'
            )
            db.add(source_column)
        
        profile.has_physical_file = False
        
        db.commit()
        
        return {
            "message": "Schema ingested successfully",
            "columns_count": len(column_names),
            "columns": column_names
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profiles/{profile_id}/source-columns")
async def get_source_columns(profile_id: int, db: Session = Depends(DuckDBClient.get_duckdb)):
    """Get source columns for a profile"""
    profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    columns = db.query(SourceColumn).filter(SourceColumn.profile_id == profile_id).all()
    
    return [{
        "id": col.id,
        "source_column": col.source_column,
        "sample_values": json.loads(col.sample_values_json or "[]"),
        "inferred_type": col.inferred_type
    } for col in columns]

@router.get("/data-model-fields")
async def get_data_model_fields(db: Session = Depends(DuckDBClient.get_duckdb)):
    """Get all data model fields"""
    fields = db.query(DataModelField).all()
    
    # Group by table
    tables = {}
    for field in fields:
        if field.model_table not in tables:
            tables[field.model_table] = []
        tables[field.model_table].append({
            "id": field.id,
            "column": field.model_column,
            "description": field.description,
            "data_type": field.data_type,
            "required": field.required,
            "unique_key": field.unique_key
        })
    
    return tables

@router.put("/profiles/{profile_id}/raw-table-name")
async def update_raw_table_name(
    profile_id: int,
    table_data: Dict[str, str],
    db: Session = Depends(DuckDBClient.get_duckdb)
):
    """Update the raw table name for warehouse connectivity"""
    profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile.raw_table_name = table_data.get("raw_table_name", "").strip()
    db.commit()
    
    return {"message": "Raw table name updated successfully"}
