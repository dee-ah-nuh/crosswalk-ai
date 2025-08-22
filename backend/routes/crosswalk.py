"""
FastAPI routes for crosswalk mapping management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import re
import json

from database import get_db
from models import SourceProfile, SourceColumn, CrosswalkMapping, RegexRule
from services.dsl_engine import DSLEngine
from services.warehouse_service import WarehouseService

router = APIRouter()

@router.get("/profiles/{profile_id}/crosswalk")
async def get_crosswalk_mappings(profile_id: int, db: Session = Depends(get_db)):
    """Get all crosswalk mappings for a profile"""
    profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Get source columns
    source_columns = db.query(SourceColumn).filter(SourceColumn.profile_id == profile_id).all()
    
    mappings_data = []
    for col in source_columns:
        # Get existing mapping
        mapping = db.query(CrosswalkMapping).filter(
            CrosswalkMapping.source_column_id == col.id
        ).first()
        
        # Get regex rules
        regex_rules = db.query(RegexRule).filter(
            RegexRule.source_column_id == col.id
        ).all()
        
        mappings_data.append({
            "source_column_id": col.id,
            "source_column": col.source_column,
            "sample_values": json.loads(col.sample_values_json or "[]"),
            "inferred_type": col.inferred_type,
            "model_table": mapping.model_table if mapping else "",
            "model_column": mapping.model_column if mapping else "",
            "is_custom_field": mapping.is_custom_field if mapping else False,
            "custom_field_name": mapping.custom_field_name if mapping else "",
            "transform_expression": mapping.transform_expression if mapping else "",
            "notes": mapping.notes if mapping else "",
            "is_mapped": bool(mapping and (mapping.model_column or mapping.custom_field_name)),
            "regex_rules": [{
                "id": rule.id,
                "rule_name": rule.rule_name,
                "pattern": rule.pattern,
                "flags": rule.flags,
                "description": rule.description
            } for rule in regex_rules]
        })
    
    return mappings_data

@router.put("/profiles/{profile_id}/crosswalk")
async def update_crosswalk_mappings(
    profile_id: int,
    mappings: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """Bulk update crosswalk mappings"""
    profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    try:
        for mapping_data in mappings:
            source_column_id = mapping_data.get("source_column_id")
            if not source_column_id:
                continue
            
            # Verify source column exists
            source_column = db.query(SourceColumn).filter(
                SourceColumn.id == source_column_id,
                SourceColumn.profile_id == profile_id
            ).first()
            
            if not source_column:
                continue
            
            # Get or create mapping
            mapping = db.query(CrosswalkMapping).filter(
                CrosswalkMapping.source_column_id == source_column_id
            ).first()
            
            if not mapping:
                mapping = CrosswalkMapping(
                    profile_id=profile_id,
                    source_column_id=source_column_id,
                    model_table="",
                    model_column=""
                )
                db.add(mapping)
            
            # Update mapping fields
            mapping.model_table = mapping_data.get("model_table", "")
            mapping.model_column = mapping_data.get("model_column", "")
            mapping.is_custom_field = mapping_data.get("is_custom_field", False)
            mapping.custom_field_name = mapping_data.get("custom_field_name", "")
            mapping.transform_expression = mapping_data.get("transform_expression", "")
            mapping.notes = mapping_data.get("notes", "")
        
        db.commit()
        return {"message": "Mappings updated successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/source-columns/{source_column_id}/regex")
async def create_regex_rule(
    source_column_id: int,
    rule_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create or update a regex rule for a source column"""
    source_column = db.query(SourceColumn).filter(SourceColumn.id == source_column_id).first()
    if not source_column:
        raise HTTPException(status_code=404, detail="Source column not found")
    
    try:
        # Validate regex pattern
        pattern = rule_data.get("pattern", "")
        if pattern:
            re.compile(pattern)  # Test if regex is valid
        
        # Create rule
        rule = RegexRule(
            source_column_id=source_column_id,
            rule_name=rule_data.get("rule_name", ""),
            pattern=pattern,
            flags=rule_data.get("flags", ""),
            description=rule_data.get("description", "")
        )
        
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        return {
            "id": rule.id,
            "rule_name": rule.rule_name,
            "pattern": rule.pattern,
            "flags": rule.flags,
            "description": rule.description
        }
        
    except re.error as e:
        raise HTTPException(status_code=400, detail=f"Invalid regex pattern: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/regex-rules/{rule_id}")
async def delete_regex_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a regex rule"""
    rule = db.query(RegexRule).filter(RegexRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Regex rule not found")
    
    db.delete(rule)
    db.commit()
    
    return {"message": "Regex rule deleted successfully"}

@router.get("/source-columns/{source_column_id}/regex/test")
async def test_regex_rule(
    source_column_id: int,
    pattern: str,
    value: str,
    flags: str = "",
    db: Session = Depends(get_db)
):
    """Test a regex pattern against a value"""
    source_column = db.query(SourceColumn).filter(SourceColumn.id == source_column_id).first()
    if not source_column:
        raise HTTPException(status_code=404, detail="Source column not found")
    
    try:
        # Parse flags
        regex_flags = 0
        if 'i' in flags.lower():
            regex_flags |= re.IGNORECASE
        if 'm' in flags.lower():
            regex_flags |= re.MULTILINE
        if 's' in flags.lower():
            regex_flags |= re.DOTALL
        
        # Test regex
        compiled_pattern = re.compile(pattern, regex_flags)
        match = compiled_pattern.search(value)
        
        result = {
            "matches": bool(match),
            "groups": [],
            "full_match": ""
        }
        
        if match:
            result["groups"] = list(match.groups())
            result["full_match"] = match.group(0)
        
        return result
        
    except re.error as e:
        raise HTTPException(status_code=400, detail=f"Invalid regex pattern: {str(e)}")

@router.get("/profiles/{profile_id}/validation-summary")
async def get_validation_summary(profile_id: int, db: Session = Depends(get_db)):
    """Get validation summary for a profile"""
    profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Get source columns
    source_columns = db.query(SourceColumn).filter(SourceColumn.profile_id == profile_id).all()
    total_columns = len(source_columns)
    
    # Count mapped columns
    mapped_columns = 0
    regex_pass_count = 0
    regex_fail_count = 0
    
    for col in source_columns:
        mapping = db.query(CrosswalkMapping).filter(
            CrosswalkMapping.source_column_id == col.id
        ).first()
        
        if mapping and (mapping.model_column or mapping.custom_field_name):
            mapped_columns += 1
        
        # Check regex rules
        regex_rules = db.query(RegexRule).filter(
            RegexRule.source_column_id == col.id
        ).all()
        
        sample_values = json.loads(col.sample_values_json or "[]")
        
        for rule in regex_rules:
            if rule.pattern and sample_values:
                try:
                    # Parse flags
                    regex_flags = 0
                    if rule.flags:
                        if 'i' in rule.flags.lower():
                            regex_flags |= re.IGNORECASE
                        if 'm' in rule.flags.lower():
                            regex_flags |= re.MULTILINE
                        if 's' in rule.flags.lower():
                            regex_flags |= re.DOTALL
                    
                    compiled_pattern = re.compile(rule.pattern, regex_flags)
                    
                    for value in sample_values:
                        if compiled_pattern.search(str(value)):
                            regex_pass_count += 1
                        else:
                            regex_fail_count += 1
                            
                except re.error:
                    regex_fail_count += len(sample_values)
    
    mapping_percentage = (mapped_columns / total_columns * 100) if total_columns > 0 else 0
    
    return {
        "total_columns": total_columns,
        "mapped_columns": mapped_columns,
        "unmapped_columns": total_columns - mapped_columns,
        "mapping_percentage": round(mapping_percentage, 1),
        "regex_pass_count": regex_pass_count,
        "regex_fail_count": regex_fail_count
    }

@router.post("/profiles/{profile_id}/sample/fetch")
async def fetch_warehouse_sample(profile_id: int, db: Session = Depends(get_db)):
    """Fetch sample data from warehouse"""
    try:
        sample_data = await WarehouseService.fetch_sample_data(db, profile_id)
        return {
            "success": True,
            "row_count": len(sample_data),
            "data": sample_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/dsl/validate")
async def validate_dsl_expression(expression_data: Dict[str, str]):
    """Validate a DSL transform expression"""
    expression = expression_data.get("expression", "")
    result = DSLEngine.validate_expression(expression)
    return result

@router.post("/dsl/translate")
async def translate_dsl_to_sql(translation_data: Dict[str, Any]):
    """Translate DSL expression to SQL"""
    expression = translation_data.get("expression", "")
    column_mapping = translation_data.get("column_mapping", {})
    
    try:
        sql_expression = DSLEngine.translate_to_sql(expression, column_mapping)
        return {
            "success": True,
            "sql_expression": sql_expression
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
