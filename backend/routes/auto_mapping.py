"""
Auto Mapping API Routes
======================

FastAPI routes for the intelligent automated mapping system.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'datascience'))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from auto_mapper import AutoMapper

router = APIRouter(prefix="/api/auto-mapping", tags=["auto-mapping"])

# Initialize the auto mapper
auto_mapper = AutoMapper()

class SourceColumnRequest(BaseModel):
    """Input model for source column data"""
    column_name: str
    sample_values: Optional[List[str]] = []
    column_order: Optional[int] = None

class MappingSuggestionResponse(BaseModel):
    """Response model for mapping suggestions"""
    source_column: str
    target_column: str
    target_table: str
    confidence: float
    reasoning: str
    data_type: str

class BulkMappingRequest(BaseModel):
    """Request model for bulk mapping suggestions"""
    source_columns: List[SourceColumnRequest]

class CorrectionRequest(BaseModel):
    """Request model for recording mapping corrections"""
    source_column: str
    correct_table: str
    correct_column: str
    incorrect_suggestion: Optional[str] = None

@router.post("/suggest", response_model=Dict[str, List[MappingSuggestionResponse]])
async def suggest_mappings(request: BulkMappingRequest):
    """
    Generate automated mapping suggestions for source columns
    
    Takes source columns with optional sample data and returns 
    intelligent suggestions from the 827-field healthcare data model.
    """
    try:
        # Convert to format expected by auto_mapper
        source_columns = [
            {
                'column_name': col.column_name,
                'sample_values': col.sample_values or []
            }
            for col in request.source_columns
        ]
        
        # Get suggestions
        suggestions = auto_mapper.bulk_suggest_mappings(source_columns)
        
        # Convert to response format
        response = {}
        for col_name, suggestion_list in suggestions.items():
            response[col_name] = [
                MappingSuggestionResponse(
                    source_column=s.source_column,
                    target_column=s.target_column,
                    target_table=s.target_table,
                    confidence=s.confidence,
                    reasoning=s.reasoning,
                    data_type=s.data_type
                )
                for s in suggestion_list
            ]
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@router.post("/correct")
async def record_correction(request: CorrectionRequest):
    """
    Record mapping correction to improve future suggestions
    
    When users confirm or correct mappings, the system learns 
    from this feedback to get smarter over time.
    """
    try:
        auto_mapper.record_correction(
            source_column=request.source_column,
            correct_table=request.correct_table,
            correct_column=request.correct_column,
            incorrect_suggestion=request.incorrect_suggestion
        )
        
        return {
            "status": "success",
            "message": f"Learned from correction: {request.source_column} → {request.correct_table}.{request.correct_column}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording correction: {str(e)}")

@router.get("/stats")
async def get_stats():
    """Get mapping system statistics"""
    try:
        return {
            "data_model_fields": len(auto_mapper.data_model_fields),
            "corrections_learned": len(auto_mapper.correction_history),
            "pattern_types": len(auto_mapper.pattern_library),
            "status": "ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@router.post("/suggest-single", response_model=List[MappingSuggestionResponse])
async def suggest_single(column_name: str, sample_values: Optional[List[str]] = None):
    """Generate suggestions for a single column"""
    try:
        suggestions = auto_mapper.generate_mapping_suggestions(column_name, sample_values or [])
        
        return [
            MappingSuggestionResponse(
                source_column=s.source_column,
                target_column=s.target_column,
                target_table=s.target_table,
                confidence=s.confidence,
                reasoning=s.reasoning,
                data_type=s.data_type
            )
            for s in suggestions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")