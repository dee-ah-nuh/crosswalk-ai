"""
Snowflake SQL Export API - Generate CREATE TABLE and INSERT statements
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
from datetime import datetime

# Import database dependency
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database import get_db
except ImportError:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable required")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

router = APIRouter(prefix="/api/snowflake", tags=["snowflake"])

class SnowflakeExport(BaseModel):
    client_id: str
    file_group: Optional[str] = None
    export_type: str  # CREATE_TABLE, INSERT_MAPPING, FULL_ETL
    table_name: str
    created_by: Optional[str] = None

@router.post("/generate-sql")
async def generate_snowflake_sql(
    export_request: SnowflakeExport,
    db: Session = Depends(get_db)
):
    """Generate Snowflake SQL based on crosswalk mappings"""
    
    try:
        # Get crosswalk mappings
        query = """
            SELECT ct.*, dm.data_type as model_data_type
            FROM crosswalk_template ct
            LEFT JOIN pi20_data_model dm ON ct.mcdm_column_name = dm.column_name
            WHERE ct.client_id = :client_id
        """
        params = {'client_id': export_request.client_id}
        
        if export_request.file_group:
            query += " AND ct.file_group_name = :file_group"
            params['file_group'] = export_request.file_group
        
        query += " AND ct.completion_status IN ('READY', 'VALIDATED') ORDER BY ct.source_column_order"
        
        mappings = db.execute(text(query), params).fetchall()
        
        if not mappings:
            raise HTTPException(status_code=404, detail="No ready mappings found")
        
        # Generate SQL based on export type
        if export_request.export_type == "CREATE_TABLE":
            sql_content = generate_create_table_sql(mappings, export_request.table_name)
        elif export_request.export_type == "INSERT_MAPPING":
            sql_content = generate_insert_mapping_sql(mappings, export_request.table_name)
        elif export_request.export_type == "FULL_ETL":
            sql_content = generate_full_etl_sql(mappings, export_request.table_name, export_request.client_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid export type")
        
        # Save export to database
        db.execute(text("""
            INSERT INTO snowflake_sql_exports 
            (client_id, file_group, export_type, sql_content, table_name, created_by)
            VALUES (:client_id, :file_group, :export_type, :sql_content, :table_name, :created_by)
        """), {
            'client_id': export_request.client_id,
            'file_group': export_request.file_group,
            'export_type': export_request.export_type,
            'sql_content': sql_content,
            'table_name': export_request.table_name,
            'created_by': export_request.created_by or 'SYSTEM'
        })
        
        db.commit()
        
        return {
            'sql_content': sql_content,
            'table_name': export_request.table_name,
            'export_type': export_request.export_type,
            'mapping_count': len(mappings)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_create_table_sql(mappings, table_name):
    """Generate CREATE TABLE SQL for Snowflake"""
    
    sql_lines = [
        f"-- Snowflake CREATE TABLE generated from crosswalk mappings",
        f"-- Generated at: {datetime.now().isoformat()}",
        f"",
        f"CREATE OR REPLACE TABLE {table_name} (",
    ]
    
    column_definitions = []
    
    for mapping in mappings:
        if not mapping.mcdm_column_name or mapping.skipped_flag:
            continue
            
        # Determine data type
        data_type = mapping.custom_data_type or mapping.inferred_data_type or mapping.model_data_type or "VARCHAR(255)"
        
        # Map to Snowflake types
        if "VARCHAR" in data_type.upper():
            snowflake_type = "STRING"
        elif "NUMBER" in data_type.upper():
            if "," in data_type:
                snowflake_type = data_type.replace("NUMBER", "NUMBER")
            else:
                snowflake_type = "NUMBER(38,0)"
        elif "DATE" in data_type.upper():
            snowflake_type = "DATE"
        elif "TIMESTAMP" in data_type.upper():
            snowflake_type = "TIMESTAMP_NTZ"
        elif "BOOLEAN" in data_type.upper():
            snowflake_type = "BOOLEAN"
        else:
            snowflake_type = "STRING"
        
        # Add column definition
        column_def = f"    {mapping.mcdm_column_name} {snowflake_type}"
        
        # Add comment if available
        if mapping.data_profile_info:
            comment = mapping.data_profile_info.replace("'", "''")[:255]  # Escape quotes and limit length
            column_def += f" COMMENT '{comment}'"
        
        column_definitions.append(column_def)
    
    # Join columns with commas
    sql_lines.extend([",\n".join(column_definitions)])
    sql_lines.append(");")
    
    # Add table comment
    sql_lines.extend([
        "",
        f"COMMENT ON TABLE {table_name} IS 'Auto-generated from crosswalk mappings - Client: {mappings[0].client_id}';",
        ""
    ])
    
    return "\n".join(sql_lines)

def generate_insert_mapping_sql(mappings, table_name):
    """Generate INSERT VALUES exactly matching the Excel formula logic for crosswalk configuration"""
    
    sql_lines = [
        f"-- Crosswalk INSERT VALUES - Exact Excel Formula Logic",
        f"-- Generated at: {datetime.now().isoformat()}",
        f"-- This matches your Excel =IF(A3=...) formula for 'Output DML for Crosswalk'",
        f"",
        f"INSERT INTO {table_name} VALUES"
    ]
    
    value_clauses = []
    
    for mapping in mappings:
        # Excel formula: IF(A3="","", ...)
        A3 = mapping.source_column_name or ""  # Source column name
        if A3 == "":
            continue  # Skip empty rows like Excel
        
        # Map database fields to Excel columns based on your formula
        B3 = mapping.source_column_order if mapping.source_column_order is not None else "NULL"  # Source column order (number)
        C3 = mapping.data_profile_info or ""  # Description (gets double quoted)
        D3 = mapping.client_id or ""  # Client ID
        E3 = mapping.in_model or ""  # MCDM table or status
        F3 = mapping.in_model or ""  # in_model flag
        G3 = mapping.mcdm_column_name or ""  # MCDM column name
        H3 = mapping.custom_field_type or ""  # Custom field type
        N3 = "NULL"  # Some numeric field (placeholder)
        O3 = mapping.mcs_review_required or False  # Boolean field
        P3 = mapping.mcs_review_required or False  # Boolean field (reusing for now)
        R3 = mapping.source_column_formatting or ""  # Additional field
        S3 = mapping.provider_file_group or ""  # Additional field
        T3 = mapping.version_notes or ""  # Additional field
        
        # Excel logic: IF(E3="NOT USED", [first format], [second format])
        if E3 == "NOT USED":
            # First format: (A3, D3, B3, C3, NULL,NULL,NULL,NULL,NULL, P3, O3, S3, T3)
            s3_val = "NULL" if S3 == "" else f"'{S3}'"
            t3_val = "NULL" if T3 == "" else f"'{T3}'"
            value_clause = f"('{A3}','{D3}',{B3},\"\"\"{C3}\"\"\",NULL,NULL,NULL,NULL,NULL,"
            value_clause += f"{'TRUE' if P3 else 'NULL'},"
            value_clause += f"{'TRUE' if O3 else 'NULL'},"
            value_clause += f"{s3_val},"
            value_clause += f"{t3_val})"
        else:
            # Main format matching your Excel formula exactly
            value_clause = f"('{A3}',"
            
            # IF(ISBLANK(D3),"NULL","'"&D3&"'")
            d3_val = "NULL" if D3 == "" else f"'{D3}'"
            value_clause += f"{d3_val},"
            
            # IF(ISBLANK(B3),"NULL",B3)  
            value_clause += f"{'NULL' if B3 == 'NULL' else B3},"
            
            # IF(ISBLANK(C3),"NULL","'"""&C3&"""'")
            c3_val = "NULL" if C3 == "" else f'"""{C3}"""'
            value_clause += f"{c3_val},"
            
            # G3 (MCDM column)
            value_clause += f"'{G3}',"
            
            # E3 (MCDM table/status)
            value_clause += f"'{E3}',"
            
            # IF(N3="","NULL",N3)
            value_clause += f"{N3},"
            
            # IF(F3="Y","NULL","'"&H3&"'")
            h3_val = "NULL" if F3 == "Y" else f"'{H3}'"
            value_clause += f"{h3_val},"
            
            # IF(R3="","NULL","'"&R3&"'")
            r3_val = "NULL" if R3 == "" else f"'{R3}'"
            value_clause += f"{r3_val},"
            
            # IF(P3=TRUE,"TRUE","NULL")
            value_clause += f"{'TRUE' if P3 else 'NULL'},"
            
            # IF(O3=TRUE,"TRUE","NULL")  
            value_clause += f"{'TRUE' if O3 else 'NULL'},"
            
            # IF(S3="","NULL","'"&S3&"'")
            s3_val = "NULL" if S3 == "" else f"'{S3}'"
            value_clause += f"{s3_val},"
            
            # IF(T3="","NULL","'"&T3&"'")
            t3_val = "NULL" if T3 == "" else f"'{T3}'"
            value_clause += f"{t3_val})"
        
        value_clauses.append(value_clause)
    
    # Join all VALUE clauses with commas (like dragging down Excel formula)
    if value_clauses:
        sql_lines.extend([",\n".join(value_clauses)])
        sql_lines.append(";")
        sql_lines.append("")
        sql_lines.append(f"-- {len(value_clauses)} crosswalk mappings generated")
        sql_lines.append("-- Each row matches your Excel formula: =IF(A3=\"\",...)")
    else:
        sql_lines.append("-- No valid mappings found")
    
    return "\n".join(sql_lines)

def generate_full_etl_sql(mappings, table_name, client_id):
    """Generate complete ETL SQL with joins and transformations"""
    
    # Group mappings by source file/table
    file_groups = {}
    for mapping in mappings:
        if mapping.skipped_flag:
            continue
        fg = mapping.file_group_name or 'DEFAULT'
        if fg not in file_groups:
            file_groups[fg] = []
        file_groups[fg].append(mapping)
    
    sql_lines = [
        f"-- Complete ETL SQL generated from crosswalk mappings",
        f"-- Client: {client_id}",
        f"-- Generated at: {datetime.now().isoformat()}",
        f"",
        f"CREATE OR REPLACE VIEW {table_name}_ETL AS",
        f"WITH"
    ]
    
    # Build CTEs for each file group
    cte_lines = []
    for i, (fg, group_mappings) in enumerate(file_groups.items()):
        cte_name = f"{fg.lower()}_data"
        cte_lines.append(f"{cte_name} AS (")
        cte_lines.append("  SELECT")
        
        select_items = []
        for mapping in group_mappings:
            if not mapping.mcdm_column_name:
                continue
                
            source_col = mapping.source_column_name
            if mapping.source_column_formatting:
                expr = mapping.source_column_formatting
            else:
                expr = source_col
            
            select_items.append(f"    {expr} AS {mapping.mcdm_column_name}")
        
        cte_lines.extend([",\n".join(select_items)])
        cte_lines.append(f"  FROM raw.{fg.lower()}_table")  # Placeholder table name
        cte_lines.append(")")
        
        if i < len(file_groups) - 1:
            cte_lines.append(",")
    
    sql_lines.extend(cte_lines)
    
    # Main SELECT with joins
    sql_lines.extend([
        "",
        "SELECT",
        "  -- Add your final SELECT columns here based on target table",
        "  *",
        f"FROM {list(file_groups.keys())[0].lower()}_data"
    ])
    
    # Add joins if multiple file groups
    if len(file_groups) > 1:
        for fg in list(file_groups.keys())[1:]:
            sql_lines.append(f"LEFT JOIN {fg.lower()}_data ON {list(file_groups.keys())[0].lower()}_data.some_sid = {fg.lower()}_data.some_sid")
    
    sql_lines.append(";")
    
    return "\n".join(sql_lines)

@router.get("/exports")
async def get_exports(
    client_id: Optional[str] = Query(None),
    export_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of Snowflake SQL exports"""
    
    query = "SELECT * FROM snowflake_sql_exports WHERE 1=1"
    params = {}
    
    if client_id:
        query += " AND client_id = :client_id"
        params['client_id'] = client_id
        
    if export_type:
        query += " AND export_type = :export_type"
        params['export_type'] = export_type
    
    query += " ORDER BY created_at DESC"
    
    exports = db.execute(text(query), params).fetchall()
    
    return [
        {
            'id': exp[0],
            'client_id': exp[1],
            'file_group': exp[2],
            'export_type': exp[3],
            'table_name': exp[5],
            'created_by': exp[6],
            'created_at': exp[7],
            'is_deployed': exp[8]
        }
        for exp in exports
    ]

@router.get("/exports/{export_id}/sql")
async def get_export_sql(export_id: int, db: Session = Depends(get_db)):
    """Get SQL content for a specific export"""
    
    result = db.execute(
        text("SELECT sql_content FROM snowflake_sql_exports WHERE id = :id"),
        {'id': export_id}
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Export not found")
    
    return {'sql_content': result[0]}