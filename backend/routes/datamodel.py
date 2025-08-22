"""
Data Model Intelligence API - provides PI20 data model assistance and validation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Import database dependency (assuming it exists in parent directory)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database import get_db
except ImportError:
    # Fallback database connection
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

router = APIRouter(prefix="/api/datamodel", tags=["datamodel"])

# Response models
class DataModelField(BaseModel):
    schema_layer: str
    table_name: str
    column_name: str
    data_type: str
    description: str
    is_standard_field: bool
    is_case_sensitive: bool

class ValidationResult(BaseModel):
    is_valid: bool
    rule_violations: List[Dict[str, Any]]
    suggestions: List[str]

class FieldSuggestion(BaseModel):
    column_name: str
    table_name: str
    schema_layer: str
    confidence_score: float
    reason: str

@router.get("/fields", response_model=List[DataModelField])
async def get_data_model_fields(
    schema_layer: Optional[str] = None,
    table_name: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get PI20 data model fields with optional filtering"""
    
    query = """
        SELECT schema_layer, table_name, column_name, data_type, 
               description, is_standard_field, is_case_sensitive
        FROM pi20_data_model
        WHERE 1=1
    """
    params = {}
    
    if schema_layer:
        query += " AND schema_layer = :schema_layer"
        params["schema_layer"] = schema_layer
    
    if table_name:
        query += " AND table_name = :table_name"
        params["table_name"] = table_name
    
    if search:
        query += " AND (column_name ILIKE :search OR description ILIKE :search)"
        params["search"] = f"%{search}%"
    
    query += " ORDER BY schema_layer, table_name, column_name"
    
    result = db.execute(text(query), params)
    
    return [
        DataModelField(
            schema_layer=row[0],
            table_name=row[1],
            column_name=row[2],
            data_type=row[3],
            description=row[4],
            is_standard_field=row[5],
            is_case_sensitive=row[6]
        )
        for row in result
    ]

@router.get("/suggest-mapping")
async def suggest_mapping(
    source_column: str,
    file_group: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[FieldSuggestion]:
    """Suggest PI20 data model fields for a source column"""
    
    suggestions = []
    
    # Exact name match
    exact_match = db.execute(
        text("SELECT schema_layer, table_name, column_name FROM pi20_data_model WHERE column_name ILIKE :column"),
        {"column": source_column}
    ).fetchall()
    
    for row in exact_match:
        suggestions.append(FieldSuggestion(
            column_name=row[2],
            table_name=row[1],
            schema_layer=row[0],
            confidence_score=1.0,
            reason="Exact column name match"
        ))
    
    # Partial matches and common patterns
    source_lower = source_column.lower()
    
    # Common patterns for healthcare data
    patterns = {
        'member': ['member_id', 'member_sid'],
        'claim': ['claim_id', 'claim_header_sid'],
        'provider': ['provider_sid', 'npi'],
        'date': ['service_from_dt', 'service_to_dt'],
        'diagnosis': ['diagnosis_1', 'diagnosis_2'],
        'procedure': ['procedure_1', 'procedure_2', 'procedure_code'],
        'amount': ['allowed_amount', 'paid_amount'],
    }
    
    for category, fields in patterns.items():
        if category in source_lower:
            for field in fields:
                field_info = db.execute(
                    text("SELECT schema_layer, table_name FROM pi20_data_model WHERE column_name = :field LIMIT 1"),
                    {"field": field}
                ).fetchone()
                
                if field_info and not any(s.column_name == field for s in suggestions):
                    suggestions.append(FieldSuggestion(
                        column_name=field,
                        table_name=field_info[1],
                        schema_layer=field_info[0],
                        confidence_score=0.8,
                        reason=f"Common pattern for {category} fields"
                    ))
    
    # Sort by confidence score
    suggestions.sort(key=lambda x: x.confidence_score, reverse=True)
    
    return suggestions[:10]  # Return top 10 suggestions

@router.post("/validate-mapping")
async def validate_mapping(
    mapping_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> ValidationResult:
    """Validate a crosswalk mapping against PI20 data model rules"""
    
    violations = []
    suggestions = []
    
    in_model = mapping_data.get('in_model', '').upper()
    mcdm_column_name = mapping_data.get('mcdm_column_name', '').strip()
    source_column_formatting = mapping_data.get('source_column_formatting', '').strip()
    custom_field_type = mapping_data.get('custom_field_type', '').strip()
    skipped_flag = mapping_data.get('skipped_flag', False)
    
    # Rule 1: IN_MODEL=Y requires MCDM column name
    if in_model == 'Y' and not mcdm_column_name:
        violations.append({
            'rule': 'IN_MODEL_Y_REQUIRES_MCDM_COLUMN',
            'message': 'Fields with IN_MODEL=Y must have an MCDM column name specified',
            'field': 'mcdm_column_name'
        })
    
    # Rule 2: Check if MCDM column requires case sensitivity handling
    if mcdm_column_name:
        case_sensitive_check = db.execute(
            text("SELECT is_case_sensitive FROM pi20_data_model WHERE column_name = :column LIMIT 1"),
            {"column": mcdm_column_name}
        ).fetchone()
        
        if case_sensitive_check and case_sensitive_check[0] and not source_column_formatting:
            violations.append({
                'rule': 'VARCHAR_FIELDS_CASE_SENSITIVITY',
                'message': f'{mcdm_column_name} is case-sensitive and requires UPPER() or LOWER() function',
                'field': 'source_column_formatting'
            })
            suggestions.append(f"Try: UPPER({mapping_data.get('source_column_name', 'column_name')})")
    
    # Rule 3: Custom fields validation
    if in_model == 'N' and not custom_field_type:
        violations.append({
            'rule': 'CUSTOM_FIELD_TYPE_VALIDATION',
            'message': 'Custom fields (IN_MODEL=N) must specify a custom field type',
            'field': 'custom_field_type'
        })
    
    # Rule 4: Skipped field logic
    if skipped_flag and in_model != 'N/A':
        violations.append({
            'rule': 'SKIPPED_FIELD_LOGIC',
            'message': 'Skipped fields should have IN_MODEL set to N/A',
            'field': 'in_model'
        })
        suggestions.append("Set IN_MODEL to 'N/A' for skipped fields")
    
    # Additional suggestions based on data model
    if mcdm_column_name and in_model == 'Y':
        field_info = db.execute(
            text("""
                SELECT schema_layer, table_name, data_type, description 
                FROM pi20_data_model 
                WHERE column_name = :column
            """),
            {"column": mcdm_column_name}
        ).fetchone()
        
        if field_info:
            schema_layer, table_name, data_type, description = field_info
            if not source_column_formatting and 'VARCHAR' in data_type:
                suggestions.append(f"Consider data type formatting for {data_type}")
            
            suggestions.append(f"Target: {schema_layer}.{table_name}.{mcdm_column_name} - {description}")
    
    is_valid = len(violations) == 0
    
    return ValidationResult(
        is_valid=is_valid,
        rule_violations=violations,
        suggestions=suggestions
    )

@router.get("/schema-layers")
async def get_schema_layers(db: Session = Depends(get_db)):
    """Get available schema layers (RAW, CLEANSE, CURATED)"""
    
    result = db.execute(
        text("SELECT DISTINCT schema_layer FROM pi20_data_model ORDER BY schema_layer")
    )
    
    return [row[0] for row in result]

@router.get("/tables")
async def get_tables(
    schema_layer: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get available tables in the data model"""
    
    query = "SELECT DISTINCT table_name FROM pi20_data_model"
    params = {}
    
    if schema_layer:
        query += " WHERE schema_layer = :schema_layer"
        params["schema_layer"] = schema_layer
    
    query += " ORDER BY table_name"
    
    result = db.execute(text(query), params)
    
    return [row[0] for row in result]

@router.get("/field-info/{column_name}")
async def get_field_info(
    column_name: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific field"""
    
    result = db.execute(
        text("""
            SELECT schema_layer, table_name, column_name, data_type, description,
                   is_standard_field, is_case_sensitive
            FROM pi20_data_model 
            WHERE column_name ILIKE :column
            ORDER BY schema_layer, table_name
        """),
        {"column": column_name}
    ).fetchall()
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Field {column_name} not found in data model")
    
    return [
        {
            "schema_layer": row[0],
            "table_name": row[1],
            "column_name": row[2],
            "data_type": row[3],
            "description": row[4],
            "is_standard_field": row[5],
            "is_case_sensitive": row[6]
        }
        for row in result
    ]