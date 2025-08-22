"""
Updated API routes for crosswalk template functionality
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Dict, Any, Optional
import json

from database import get_db

router = APIRouter()

@router.get("/crosswalk")
async def get_crosswalk_data(
    client_id: Optional[str] = Query(None),
    file_group: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Get crosswalk template data with filtering"""
    
    # Build base query
    query = """
        SELECT 
            id, client_id, source_column_order, source_column_name, file_group_name,
            mcdm_column_name, in_model, mcdm_table, custom_field_type,
            data_profile_info, profile_column_2, profile_column_3, profile_column_4,
            profile_column_5, profile_column_6, source_column_formatting, skipped_flag,
            additional_field_1, additional_field_2, additional_field_3, additional_field_4,
            additional_field_5, additional_field_6, additional_field_7, additional_field_8,
            created_at, updated_at
        FROM crosswalk_template
        WHERE 1=1
    """
    params = {}
    
    if client_id:
        query += " AND client_id = :client_id"
        params['client_id'] = client_id
    
    if file_group:
        query += " AND file_group_name = :file_group"
        params['file_group'] = file_group
    
    query += " ORDER BY source_column_order, source_column_name"
    query += " LIMIT :limit OFFSET :offset"
    params['limit'] = limit
    params['offset'] = offset
    
    result = db.execute(text(query), params).fetchall()
    
    # Convert to list of dictionaries
    columns = [
        'id', 'client_id', 'source_column_order', 'source_column_name', 'file_group_name',
        'mcdm_column_name', 'in_model', 'mcdm_table', 'custom_field_type',
        'data_profile_info', 'profile_column_2', 'profile_column_3', 'profile_column_4',
        'profile_column_5', 'profile_column_6', 'source_column_formatting', 'skipped_flag',
        'additional_field_1', 'additional_field_2', 'additional_field_3', 'additional_field_4',
        'additional_field_5', 'additional_field_6', 'additional_field_7', 'additional_field_8',
        'created_at', 'updated_at'
    ]
    
    data = []
    for row in result:
        row_dict = {}
        for i, col in enumerate(columns):
            row_dict[col] = row[i]
        data.append(row_dict)
    
    return {
        "data": data,
        "total": len(data),
        "offset": offset,
        "limit": limit
    }

@router.post("/crosswalk/{mapping_id}/duplicate")
async def duplicate_crosswalk_mapping(
    mapping_id: int,
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Duplicate a crosswalk mapping with new table assignment"""
    
    # Get the original mapping
    original = db.execute(
        text("SELECT * FROM crosswalk_template WHERE id = :id"),
        {'id': mapping_id}
    ).fetchone()
    
    if not original:
        raise HTTPException(status_code=404, detail="Original mapping not found")
    
    # Create new mapping with duplicated data
    new_table = data.get('mcdm_table', original[7])  # mcdm_table is column 7
    
    insert_query = """
        INSERT INTO crosswalk_template (
            client_id, source_column_order, source_column_name, file_group_name,
            mcdm_column_name, in_model, mcdm_table, custom_field_type,
            data_profile_info, profile_column_2, profile_column_3, profile_column_4,
            profile_column_5, profile_column_6, source_column_formatting, skipped_flag,
            additional_field_1, additional_field_2, additional_field_3, additional_field_4,
            additional_field_5, additional_field_6, additional_field_7, additional_field_8,
            created_at, updated_at
        ) VALUES (
            :client_id, :source_column_order, :source_column_name, :file_group_name,
            :mcdm_column_name, :in_model, :mcdm_table, :custom_field_type,
            :data_profile_info, :profile_column_2, :profile_column_3, :profile_column_4,
            :profile_column_5, :profile_column_6, :source_column_formatting, :skipped_flag,
            :additional_field_1, :additional_field_2, :additional_field_3, :additional_field_4,
            :additional_field_5, :additional_field_6, :additional_field_7, :additional_field_8,
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        )
        RETURNING id
    """
    
    # Prepare data for new mapping
    new_mapping_data = {
        'client_id': original[1],
        'source_column_order': original[2],
        'source_column_name': original[3],
        'file_group_name': original[4],
        'mcdm_column_name': original[5],
        'in_model': original[6],
        'mcdm_table': new_table,
        'custom_field_type': original[8],
        'data_profile_info': original[9],
        'profile_column_2': original[10],
        'profile_column_3': original[11],
        'profile_column_4': original[12],
        'profile_column_5': original[13],
        'profile_column_6': original[14],
        'source_column_formatting': original[15],
        'skipped_flag': original[16],
        'additional_field_1': original[17],
        'additional_field_2': original[18],
        'additional_field_3': original[19],
        'additional_field_4': original[20],
        'additional_field_5': original[21],
        'additional_field_6': original[22],
        'additional_field_7': original[23],
        'additional_field_8': original[24]
    }
    
    result = db.execute(text(insert_query), new_mapping_data)
    new_id = result.fetchone()[0]
    db.commit()
    
    return {"success": True, "message": "Mapping duplicated successfully", "new_id": new_id}

@router.put("/crosswalk/{mapping_id}")
async def update_crosswalk_mapping(
    mapping_id: int,
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update a crosswalk mapping"""
    
    # Check if mapping exists
    existing = db.execute(
        text("SELECT id FROM crosswalk_template WHERE id = :id"),
        {'id': mapping_id}
    ).fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    # Build update query dynamically based on provided fields
    allowed_fields = [
        'client_id', 'source_column_order', 'source_column_name', 'file_group_name',
        'mcdm_column_name', 'in_model', 'mcdm_table', 'custom_field_type',
        'data_profile_info', 'profile_column_2', 'profile_column_3', 'profile_column_4',
        'profile_column_5', 'profile_column_6', 'source_column_formatting', 'skipped_flag',
        'additional_field_1', 'additional_field_2', 'additional_field_3', 'additional_field_4',
        'additional_field_5', 'additional_field_6', 'additional_field_7', 'additional_field_8'
    ]
    
    updates = []
    params = {'id': mapping_id}
    
    for field, value in data.items():
        if field in allowed_fields:
            updates.append(f"{field} = :{field}")
            params[field] = value
    
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    # Add updated_at
    updates.append("updated_at = CURRENT_TIMESTAMP")
    
    update_query = f"""
        UPDATE crosswalk_template 
        SET {', '.join(updates)}
        WHERE id = :id
    """
    
    db.execute(text(update_query), params)
    db.commit()
    
    return {"success": True, "message": "Mapping updated successfully"}

@router.get("/crosswalk/clients")
async def get_clients(db: Session = Depends(get_db)):
    """Get list of unique clients"""
    result = db.execute(text("""
        SELECT DISTINCT client_id, COUNT(*) as mapping_count
        FROM crosswalk_template 
        WHERE client_id IS NOT NULL AND client_id != ''
        GROUP BY client_id
        ORDER BY client_id
    """)).fetchall()
    
    return [{"client_id": row[0], "mapping_count": row[1]} for row in result]

@router.get("/crosswalk/file-groups")
async def get_file_groups(
    client_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of file groups, optionally filtered by client"""
    query = """
        SELECT DISTINCT file_group_name, COUNT(*) as mapping_count
        FROM crosswalk_template 
        WHERE file_group_name IS NOT NULL AND file_group_name != ''
    """
    params = {}
    
    if client_id:
        query += " AND client_id = :client_id"
        params['client_id'] = client_id
    
    query += " GROUP BY file_group_name ORDER BY file_group_name"
    
    result = db.execute(text(query), params).fetchall()
    
    return [{"file_group": row[0], "mapping_count": row[1]} for row in result]

@router.get("/crosswalk/summary")
async def get_crosswalk_summary(db: Session = Depends(get_db)):
    """Get summary statistics for the crosswalk data"""
    
    # Get basic counts
    total_mappings = db.execute(text("SELECT COUNT(*) FROM crosswalk_template")).scalar()
    total_clients = db.execute(text("SELECT COUNT(DISTINCT client_id) FROM crosswalk_template WHERE client_id IS NOT NULL")).scalar()
    total_file_groups = db.execute(text("SELECT COUNT(DISTINCT file_group_name) FROM crosswalk_template WHERE file_group_name IS NOT NULL")).scalar()
    
    # Get in_model distribution
    in_model_stats = db.execute(text("""
        SELECT in_model, COUNT(*) as count
        FROM crosswalk_template 
        GROUP BY in_model
        ORDER BY count DESC
    """)).fetchall()
    
    # Get skipped fields count
    skipped_count = db.execute(text("SELECT COUNT(*) FROM crosswalk_template WHERE skipped_flag = true")).scalar()
    
    # Get file group distribution
    file_group_stats = db.execute(text("""
        SELECT file_group_name, COUNT(*) as count
        FROM crosswalk_template 
        GROUP BY file_group_name
        ORDER BY count DESC
        LIMIT 10
    """)).fetchall()
    
    return {
        "total_mappings": total_mappings,
        "total_clients": total_clients,
        "total_file_groups": total_file_groups,
        "skipped_fields": skipped_count,
        "in_model_distribution": [{"in_model": row[0], "count": row[1]} for row in in_model_stats],
        "file_group_distribution": [{"file_group": row[0], "count": row[1]} for row in file_group_stats]
    }

@router.post("/crosswalk/search")
async def search_crosswalk(
    search_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Advanced search in crosswalk data"""
    
    search_term = search_data.get('term', '').strip()
    search_fields = search_data.get('fields', ['source_column_name', 'mcdm_column_name'])
    
    if not search_term:
        return {"data": [], "total": 0}
    
    # Build search query
    conditions = []
    params = {}
    
    for i, field in enumerate(search_fields):
        if field in ['source_column_name', 'mcdm_column_name', 'data_profile_info', 'source_column_formatting']:
            param_name = f'search_term_{i}'
            conditions.append(f"{field} ILIKE :%{param_name}%")
            params[param_name] = f"%{search_term}%"
    
    if not conditions:
        return {"data": [], "total": 0}
    
    query = f"""
        SELECT 
            id, client_id, source_column_order, source_column_name, file_group_name,
            mcdm_column_name, in_model, mcdm_table, data_profile_info
        FROM crosswalk_template
        WHERE ({' OR '.join(conditions)})
        ORDER BY source_column_order, source_column_name
        LIMIT 50
    """
    
    result = db.execute(text(query), params).fetchall()
    
    data = []
    for row in result:
        data.append({
            'id': row[0],
            'client_id': row[1],
            'source_column_order': row[2],
            'source_column_name': row[3],
            'file_group_name': row[4],
            'mcdm_column_name': row[5],
            'in_model': row[6],
            'mcdm_table': row[7],
            'data_profile_info': row[8]
        })
    
    return {
        "data": data,
        "total": len(data)
    }