"""
API Integration for Automated Mapping System
===========================================

FastAPI endpoints to integrate the auto-mapper with the crosswalk application.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from .auto_mapper import AutoMapper, MappingSuggestion
import json

router = APIRouter()

# Initialize the auto mapper
auto_mapper = AutoMapper()

class SourceColumn(BaseModel):
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
    source_columns: List[SourceColumn]

class CorrectionRequest(BaseModel):
    """Request model for recording mapping corrections"""
    source_column: str
    correct_table: str
    correct_column: str
    incorrect_suggestion: Optional[str] = None

@router.post("/suggest-mappings")
async def suggest_mappings(request: BulkMappingRequest) -> Dict[str, List[MappingSuggestionResponse]]:
    """
    Generate automated mapping suggestions for source columns
    
    This endpoint takes a list of source columns with optional sample data
    and returns intelligent mapping suggestions to the data model fields.
    """
    try:
        # Convert input to format expected by auto_mapper
        source_columns = [
            {
                'column_name': col.column_name,
                'sample_values': col.sample_values or []
            }
            for col in request.source_columns
        ]
        
        # Get suggestions from auto mapper
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

@router.post("/record-correction")
async def record_correction(request: CorrectionRequest) -> Dict[str, str]:
    """
    Record a user correction to improve future mapping suggestions
    
    When users correct/confirm mappings, this endpoint learns from the feedback
    to improve future suggestions through machine learning.
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
            "message": f"Recorded correction for {request.source_column}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording correction: {str(e)}")

@router.get("/mapping-stats")
async def get_mapping_stats() -> Dict[str, int]:
    """Get statistics about the mapping system"""
    try:
        stats = {
            "data_model_fields": len(auto_mapper.data_model_fields),
            "correction_history_count": len(auto_mapper.correction_history),
            "pattern_types": len(auto_mapper.pattern_library)
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@router.post("/suggest-single")
async def suggest_single_mapping(column_name: str, sample_values: Optional[List[str]] = None) -> List[MappingSuggestionResponse]:
    """
    Generate mapping suggestions for a single column
    """
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
        raise HTTPException(status_code=500, detail=f"Error generating single suggestion: {str(e)}")