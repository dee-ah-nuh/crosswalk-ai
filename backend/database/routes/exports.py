"""
FastAPI routes for export functionality.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import StringIO, BytesIO
import json

from database.duckdb_cxn import DuckDBClient
from services.export_service import ExportService

router = APIRouter()

@router.get("/profiles/{profile_id}/export/csv")
async def export_crosswalk_csv(profile_id: int, db: Session = Depends(DuckDBClient.get_duckdb)):
    """Export crosswalk as CSV"""
    try:
        csv_content = ExportService.export_crosswalk_csv(db, profile_id)
        
        return StreamingResponse(
            StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=crosswalk_{profile_id}.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profiles/{profile_id}/export/xlsx")
async def export_crosswalk_excel(profile_id: int, db: Session = Depends(DuckDBClient.get_duckdb)):
    """Export crosswalk as Excel"""
    try:
        excel_content = ExportService.export_crosswalk_excel(db, profile_id)
        
        return StreamingResponse(
            BytesIO(excel_content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=crosswalk_{profile_id}.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profiles/{profile_id}/export/json")
async def export_json_config(profile_id: int, db: Session = Depends(DuckDBClient.get_duckdb)):
    """Export crosswalk as JSON configuration"""
    try:
        json_config = ExportService.export_json_config(db, profile_id)
        
        return StreamingResponse(
            StringIO(json.dumps(json_config, indent=2)),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=crosswalk_{profile_id}.json"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profiles/{profile_id}/export/sql")
async def export_sql_script(profile_id: int, db: Session = Depends(DuckDBClient.get_duckdb)):
    """Export crosswalk as SQL script"""
    try:
        sql_script = ExportService.export_sql_script(db, profile_id)
        
        return StreamingResponse(
            StringIO(sql_script),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=crosswalk_{profile_id}.sql"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
