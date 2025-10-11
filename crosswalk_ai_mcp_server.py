"""
CrosswalkAI MCP Server
======================

This MCP server exposes the complete CrosswalkAI application functionality
through the Model Context Protocol, enabling AI agents to interact with
the healthcare data crosswalk and ETL helper system.

Tools available:
- Profile management (create, list, manage source profiles)
- Column mapping and crosswalk operations
- Auto-mapping suggestions using AI/ML
- Data model operations and field information
- Export functionality (CSV, Excel, JSON, SQL)
- Snowflake deployment script generation
- File parsing and schema ingestion

Resources available:
- PI20 data model fields
- Source profiles with columns
- Crosswalk mappings
- Export configurations
"""

import os
import sys
import json
import asyncio
import logging
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import duckdb
from sqlalchemy.orm import Session
from fastmcp import FastMCP

# Import your existing models and services
try:
    from database.duckdb_cxn import DuckDBClient
    from database.models import (
        SourceProfile, SourceColumn, CrosswalkMapping, 
        DataModelField, RegexRule, WarehouseConfig
    )
    from datascience.auto_mapper import AutoMapper, MappingSuggestion
    from services.file_parser import FileParser
    from services.export_service import ExportService
    from services.dsl_engine import DSLEngine
except ImportError as e:
    logging.warning(f"Import error: {e}. Some functionality may be limited.")
    SourceProfile = SourceColumn = CrosswalkMapping = None
    DataModelField = RegexRule = WarehouseConfig = None
    AutoMapper = FileParser = ExportService = DSLEngine = None

# Initialize FastMCP server
mcp = FastMCP("CrosswalkAI - Healthcare Data Engineering Assistant")

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "database", "crosswalk.duckdb")
DB_URL = f"duckdb:///{DB_PATH}"

def get_db_session():
    """Get database session"""
    try:
        return DuckDBClient.get_duckdb()
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None

def execute_query(query: str, params: tuple = None) -> List[Dict]:
    """Execute raw SQL query and return results"""
    try:
        conn = duckdb.connect(DB_PATH)
        if params:
            result = conn.execute(query, params).fetchall()
        else:
            result = conn.execute(query).fetchall()
        
        # Get column names
        columns = [desc[0] for desc in conn.description] if conn.description else []
        
        # Convert to list of dictionaries
        rows = []
        for row in result:
            rows.append(dict(zip(columns, row)))
        
        conn.close()
        return rows
    except Exception as e:
        logging.error(f"Query execution error: {e}")
        return [{"error": str(e)}]

# Initialize services
auto_mapper = AutoMapper(DB_URL) if AutoMapper else None
file_parser = FileParser() if FileParser else None
export_service = ExportService() if ExportService else None

# =============================================================================
# PROFILE MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
def create_profile(name: str, client_id: str = "") -> Dict[str, Any]:
    """
    Create a new source data profile for crosswalk mapping.
    
    Args:
        name: Name for the new profile (required)
        client_id: Optional client identifier
    
    Returns:
        Created profile details including ID
    """
    try:
        db = get_db_session()
        if not db:
            return {"error": "Database connection failed"}
        
        profile = SourceProfile(
            name=name,
            client_id=client_id if client_id else None
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        return {
            "id": profile.id,
            "name": profile.name,
            "client_id": profile.client_id,
            "created_at": str(profile.created_at)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def list_profiles() -> List[Dict[str, Any]]:
    """
    List all source profiles in the system.
    
    Returns:
        List of all profiles with their details
    """
    try:
        query = """
            SELECT id, name, client_id, created_at, updated_at, 
                   has_physical_file, raw_table_name
            FROM source_profiles 
            ORDER BY created_at DESC
        """
        return execute_query(query)
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_profile_details(profile_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific profile.
    
    Args:
        profile_id: ID of the profile to retrieve
        
    Returns:
        Profile details with associated columns and mappings count
    """
    try:
        query = """
            SELECT p.id, p.name, p.client_id, p.created_at, p.updated_at,
                   p.has_physical_file, p.raw_table_name,
                   COUNT(DISTINCT sc.id) as column_count,
                   COUNT(DISTINCT cm.id) as mapping_count
            FROM source_profiles p
            LEFT JOIN source_columns sc ON p.id = sc.profile_id
            LEFT JOIN crosswalk_mappings cm ON p.id = cm.profile_id
            WHERE p.id = ?
            GROUP BY p.id, p.name, p.client_id, p.created_at, p.updated_at,
                     p.has_physical_file, p.raw_table_name
        """
        results = execute_query(query, (profile_id,))
        return results[0] if results else {"error": "Profile not found"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_profile_source_columns(profile_id: int) -> List[Dict[str, Any]]:
    """
    Get all source columns for a specific profile.
    
    Args:
        profile_id: ID of the profile
        
    Returns:
        List of source columns with their details
    """
    try:
        query = """
            SELECT id, source_column, sample_values_json, inferred_type
            FROM source_columns 
            WHERE profile_id = ?
            ORDER BY source_column
        """
        return execute_query(query, (profile_id,))
    except Exception as e:
        return [{"error": str(e)}]

# =============================================================================
# DATA MODEL TOOLS
# =============================================================================

@mcp.tool()
def search_pi20_fields(search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search PI20 data model fields by name or description.
    
    Args:
        search_term: Text to search for in field names or descriptions
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of matching PI20 data model fields
    """
    try:
        query = """
            SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT, 
                   IS_MANDATORY, MANDATORY_PROV_TYPE, MCDM_MASKING_TYPE
            FROM pi20_data_model
            WHERE COLUMN_NAME ILIKE ? OR COLUMN_COMMENT ILIKE ?
            ORDER BY COLUMN_NAME
            LIMIT ?
        """
        search_pattern = f"%{search_term}%"
        return execute_query(query, (search_pattern, search_pattern, limit))
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_pi20_field_details(field_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific PI20 data model field.
    
    Args:
        field_name: The exact name of the PI20 field
    
    Returns:
        Detailed field information including type, description, and validation rules
    """
    try:
        query = """
            SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_ORDER, 
                   COLUMN_COMMENT, TABLE_CREATION_ORDER, IS_MANDATORY, 
                   MANDATORY_PROV_TYPE, MCDM_MASKING_TYPE, IN_EDITS, KEY
            FROM pi20_data_model
            WHERE COLUMN_NAME = ?
        """
        results = execute_query(query, (field_name,))
        return results[0] if results else {"error": f"Field '{field_name}' not found"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def list_all_pi20_fields() -> List[Dict[str, Any]]:
    """
    List all available PI20 data model fields.
    
    Returns:
        List of all PI20 fields with basic information
    """
    try:
        query = """
            SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT, IS_MANDATORY
            FROM pi20_data_model
            ORDER BY TABLE_NAME, COLUMN_ORDER
        """
        return execute_query(query)
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_pi20_tables() -> List[Dict[str, Any]]:
    """
    Get list of all tables in the PI20 data model.
    
    Returns:
        List of tables with field counts
    """
    try:
        query = """
            SELECT TABLE_NAME, COUNT(*) as field_count,
                   MIN(TABLE_CREATION_ORDER) as creation_order
            FROM pi20_data_model
            GROUP BY TABLE_NAME
            ORDER BY creation_order
        """
        return execute_query(query)
    except Exception as e:
        return [{"error": str(e)}]

# =============================================================================
# AUTO-MAPPING TOOLS
# =============================================================================

@mcp.tool()
def suggest_mappings(source_columns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get intelligent mapping suggestions for source columns to PI20 fields.
    
    Args:
        source_columns: List of dicts with 'column_name' and optional 'sample_values'
            Example: [{"column_name": "MEMBER_ID", "sample_values": ["12345", "67890"]}]
    
    Returns:
        Dictionary mapping each source column to suggested PI20 fields with confidence scores
    """
    try:
        if not auto_mapper:
            return {"error": "AutoMapper not available"}
        
        suggestions = auto_mapper.bulk_suggest_mappings(source_columns)
        
        result = {}
        for col_name, suggestion_list in suggestions.items():
            result[col_name] = [
                {
                    "target_column": s.target_column,
                    "target_table": s.target_table,
                    "confidence": round(s.confidence, 3),
                    "reasoning": s.reasoning,
                    "data_type": s.data_type
                }
                for s in suggestion_list
            ]
        
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def suggest_single_mapping(column_name: str, sample_values: str = "") -> List[Dict[str, Any]]:
    """
    Get mapping suggestions for a single source column.
    
    Args:
        column_name: Name of the source column
        sample_values: Optional sample values (comma-separated)
        
    Returns:
        List of mapping suggestions with confidence scores
    """
    try:
        if not auto_mapper:
            return [{"error": "AutoMapper not available"}]
        
        column_info = {"column_name": column_name}
        if sample_values:
            column_info["sample_values"] = sample_values.split(",")
        
        suggestions = auto_mapper.suggest_mapping(column_info)
        
        return [
            {
                "target_column": s.target_column,
                "target_table": s.target_table,
                "confidence": round(s.confidence, 3),
                "reasoning": s.reasoning,
                "data_type": s.data_type
            }
            for s in suggestions
        ]
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def add_mapping_correction(
    source_column: str,
    incorrect_suggestion: str,
    correct_mapping: str,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Add a correction to improve future mapping suggestions.
    
    Args:
        source_column: Name of the source column
        incorrect_suggestion: The field that was incorrectly suggested
        correct_mapping: The correct target field
        notes: Optional notes about the correction
        
    Returns:
        Confirmation of correction added
    """
    try:
        if not auto_mapper:
            return {"error": "AutoMapper not available"}
        
        auto_mapper.add_correction(source_column, incorrect_suggestion, correct_mapping)
        
        return {
            "status": "success",
            "message": f"Correction added: {source_column} -> {correct_mapping}",
            "notes": notes
        }
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# CROSSWALK MAPPING TOOLS
# =============================================================================

@mcp.tool()
def create_crosswalk_mapping(
    profile_id: int,
    source_column_id: int,
    target_table: str,
    target_column: str,
    transform_expression: str = "",
    notes: str = ""
) -> Dict[str, Any]:
    """
    Create a crosswalk mapping from source column to PI20 target field.
    
    Args:
        profile_id: ID of the source profile
        source_column_id: ID of the source column
        target_table: Name of the target table
        target_column: Name of the target column
        transform_expression: Optional transformation logic
        notes: Optional mapping notes
    
    Returns:
        Created mapping details
    """
    try:
        db = get_db_session()
        if not db:
            return {"error": "Database connection failed"}
        
        mapping = CrosswalkMapping(
            profile_id=profile_id,
            source_column_id=source_column_id,
            model_table=target_table,
            model_column=target_column,
            transform_expression=transform_expression,
            notes=notes
        )
        
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        
        return {
            "id": mapping.id,
            "profile_id": mapping.profile_id,
            "source_column_id": mapping.source_column_id,
            "target_table": mapping.model_table,
            "target_column": mapping.model_column,
            "transform_expression": mapping.transform_expression,
            "notes": mapping.notes
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_crosswalk_mappings(profile_id: int = None) -> List[Dict[str, Any]]:
    """
    Get crosswalk mappings, optionally filtered by profile.
    
    Args:
        profile_id: Optional profile ID to filter mappings
        
    Returns:
        List of crosswalk mappings with details
    """
    try:
        if profile_id:
            query = """
                SELECT cm.id, cm.profile_id, cm.source_column_id, cm.model_table, 
                       cm.model_column, cm.transform_expression, cm.notes,
                       sc.source_column, p.name as profile_name
                FROM crosswalk_mappings cm
                JOIN source_columns sc ON cm.source_column_id = sc.id
                JOIN source_profiles p ON cm.profile_id = p.id
                WHERE cm.profile_id = ?
                ORDER BY sc.source_column
            """
            return execute_query(query, (profile_id,))
        else:
            query = """
                SELECT cm.id, cm.profile_id, cm.source_column_id, cm.model_table, 
                       cm.model_column, cm.transform_expression, cm.notes,
                       sc.source_column, p.name as profile_name
                FROM crosswalk_mappings cm
                JOIN source_columns sc ON cm.source_column_id = sc.id
                JOIN source_profiles p ON cm.profile_id = p.id
                ORDER BY p.name, sc.source_column
            """
            return execute_query(query)
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def update_crosswalk_mapping(
    mapping_id: int,
    target_table: str = None,
    target_column: str = None,
    transform_expression: str = None,
    notes: str = None
) -> Dict[str, Any]:
    """
    Update an existing crosswalk mapping.
    
    Args:
        mapping_id: ID of the mapping to update
        target_table: New target table (optional)
        target_column: New target column (optional)
        transform_expression: New transformation logic (optional)
        notes: New notes (optional)
        
    Returns:
        Updated mapping details
    """
    try:
        db = get_db_session()
        if not db:
            return {"error": "Database connection failed"}
        
        mapping = db.query(CrosswalkMapping).filter(CrosswalkMapping.id == mapping_id).first()
        if not mapping:
            return {"error": "Mapping not found"}
        
        if target_table is not None:
            mapping.model_table = target_table
        if target_column is not None:
            mapping.model_column = target_column
        if transform_expression is not None:
            mapping.transform_expression = transform_expression
        if notes is not None:
            mapping.notes = notes
        
        db.commit()
        db.refresh(mapping)
        
        return {
            "id": mapping.id,
            "target_table": mapping.model_table,
            "target_column": mapping.model_column,
            "transform_expression": mapping.transform_expression,
            "notes": mapping.notes
        }
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# FILE PROCESSING TOOLS
# =============================================================================

@mcp.tool()
def ingest_schema_from_text(profile_id: int, schema_text: str) -> Dict[str, Any]:
    """
    Parse and ingest schema information from text.
    
    Args:
        profile_id: ID of the profile to add columns to
        schema_text: Schema definition text
        
    Returns:
        Summary of columns added
    """
    try:
        if not file_parser:
            return {"error": "File parser not available"}
        
        # Parse schema text to extract columns
        columns = file_parser.parse_schema_text(schema_text)
        
        db = get_db_session()
        if not db:
            return {"error": "Database connection failed"}
        
        added_count = 0
        for col_info in columns:
            source_column = SourceColumn(
                profile_id=profile_id,
                source_column=col_info.get('column_name'),
                inferred_type=col_info.get('data_type', 'varchar'),
                sample_values_json=json.dumps(col_info.get('sample_values', []))
            )
            db.add(source_column)
            added_count += 1
        
        db.commit()
        
        return {
            "status": "success",
            "profile_id": profile_id,
            "columns_added": added_count,
            "columns": columns
        }
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# EXPORT TOOLS
# =============================================================================

@mcp.tool()
def export_crosswalk_csv(profile_id: int) -> Dict[str, Any]:
    """
    Export crosswalk mappings for a profile as CSV format.
    
    Args:
        profile_id: ID of the profile to export
        
    Returns:
        CSV content and metadata
    """
    try:
        query = """
            SELECT sc.source_column, cm.model_table, cm.model_column,
                   cm.transform_expression, cm.notes, sc.inferred_type,
                   sc.sample_values_json
            FROM crosswalk_mappings cm
            JOIN source_columns sc ON cm.source_column_id = sc.id
            WHERE cm.profile_id = ?
            ORDER BY sc.source_column
        """
        
        mappings = execute_query(query, (profile_id,))
        
        if not mappings or "error" in mappings[0]:
            return {"error": "No mappings found or query failed"}
        
        # Convert to CSV format
        csv_lines = ["Source Column,Target Table,Target Column,Transform Expression,Notes,Data Type,Sample Values"]
        
        for mapping in mappings:
            line = f"{mapping['source_column']},{mapping['model_table']},{mapping['model_column']}," \
                   f"{mapping['transform_expression'] or ''},{mapping['notes'] or ''}," \
                   f"{mapping['inferred_type'] or ''},{mapping['sample_values_json'] or ''}"
            csv_lines.append(line)
        
        csv_content = "\n".join(csv_lines)
        
        return {
            "format": "csv",
            "profile_id": profile_id,
            "content": csv_content,
            "row_count": len(mappings)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def export_crosswalk_json(profile_id: int) -> Dict[str, Any]:
    """
    Export crosswalk mappings for a profile as JSON format.
    
    Args:
        profile_id: ID of the profile to export
        
    Returns:
        JSON content and metadata
    """
    try:
        query = """
            SELECT sc.source_column, cm.model_table, cm.model_column,
                   cm.transform_expression, cm.notes, sc.inferred_type,
                   sc.sample_values_json
            FROM crosswalk_mappings cm
            JOIN source_columns sc ON cm.source_column_id = sc.id
            WHERE cm.profile_id = ?
            ORDER BY sc.source_column
        """
        
        mappings = execute_query(query, (profile_id,))
        
        if not mappings or "error" in mappings[0]:
            return {"error": "No mappings found or query failed"}
        
        # Convert sample_values_json from string to actual JSON
        for mapping in mappings:
            try:
                if mapping.get('sample_values_json'):
                    mapping['sample_values'] = json.loads(mapping['sample_values_json'])
                del mapping['sample_values_json']  # Remove the string version
            except:
                mapping['sample_values'] = []
        
        return {
            "format": "json",
            "profile_id": profile_id,
            "mappings": mappings,
            "count": len(mappings)
        }
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# SNOWFLAKE DEPLOYMENT TOOLS
# =============================================================================

@mcp.tool()
def generate_snowflake_sql(profile_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Snowflake deployment SQL scripts.
    
    Args:
        profile_id: ID of the profile to generate SQL for
        config: Snowflake configuration (database, schema, warehouse, etc.)
        
    Returns:
        Generated SQL scripts and deployment instructions
    """
    try:
        # Get mappings for the profile
        mappings = get_crosswalk_mappings(profile_id)
        if not mappings or "error" in mappings[0]:
            return {"error": "No mappings found for profile"}
        
        # Generate CREATE TABLE statement
        table_name = config.get('table_name', f'profile_{profile_id}_data')
        database = config.get('database', 'ANALYTICS')
        schema = config.get('schema', 'STAGING')
        
        create_table_sql = f"CREATE OR REPLACE TABLE {database}.{schema}.{table_name} (\n"
        
        columns = []
        for mapping in mappings:
            col_name = mapping['model_column']
            # Infer Snowflake data type
            data_type = mapping.get('inferred_type', 'VARCHAR')
            if data_type.lower() in ['int', 'integer']:
                sf_type = 'NUMBER'
            elif data_type.lower() in ['float', 'double', 'decimal']:
                sf_type = 'FLOAT'
            elif data_type.lower() in ['date']:
                sf_type = 'DATE'
            elif data_type.lower() in ['timestamp', 'datetime']:
                sf_type = 'TIMESTAMP'
            else:
                sf_type = 'VARCHAR(255)'
            
            columns.append(f"    {col_name} {sf_type}")
        
        create_table_sql += ",\n".join(columns) + "\n);"
        
        # Generate INSERT statement with transformations
        insert_sql = f"INSERT INTO {database}.{schema}.{table_name} (\n"
        insert_sql += "    " + ", ".join([m['model_column'] for m in mappings]) + "\n"
        insert_sql += ") SELECT\n"
        
        select_clauses = []
        for mapping in mappings:
            source_col = mapping['source_column']
            transform = mapping.get('transform_expression')
            
            if transform:
                select_clauses.append(f"    {transform} as {mapping['model_column']}")
            else:
                select_clauses.append(f"    {source_col} as {mapping['model_column']}")
        
        insert_sql += ",\n".join(select_clauses)
        insert_sql += f"\nFROM {database}.{schema}.source_table;"
        
        return {
            "profile_id": profile_id,
            "database": database,
            "schema": schema,
            "table_name": table_name,
            "create_table_sql": create_table_sql,
            "insert_sql": insert_sql,
            "mapping_count": len(mappings)
        }
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# SYSTEM TOOLS
# =============================================================================

@mcp.tool()
def get_system_stats() -> Dict[str, Any]:
    """
    Get comprehensive system statistics and health information.
    
    Returns:
        System statistics including counts, health status, and configuration
    """
    try:
        stats = {}
        
        # Profile statistics
        profile_query = "SELECT COUNT(*) as count FROM source_profiles"
        profile_result = execute_query(profile_query)
        stats['total_profiles'] = profile_result[0]['count'] if profile_result else 0
        
        # Column statistics
        column_query = "SELECT COUNT(*) as count FROM source_columns"
        column_result = execute_query(column_query)
        stats['total_source_columns'] = column_result[0]['count'] if column_result else 0
        
        # Mapping statistics
        mapping_query = "SELECT COUNT(*) as count FROM crosswalk_mappings"
        mapping_result = execute_query(mapping_query)
        stats['total_mappings'] = mapping_result[0]['count'] if mapping_result else 0
        
        # PI20 field count
        pi20_query = "SELECT COUNT(*) as count FROM pi20_data_model"
        pi20_result = execute_query(pi20_query)
        stats['pi20_fields'] = pi20_result[0]['count'] if pi20_result else 0
        
        # Auto-mapper status
        if auto_mapper:
            stats['auto_mapper_status'] = 'available'
            stats['auto_mapper_corrections'] = len(getattr(auto_mapper, 'correction_history', []))
        else:
            stats['auto_mapper_status'] = 'not_available'
        
        # Service availability
        stats['services'] = {
            'auto_mapper': auto_mapper is not None,
            'file_parser': file_parser is not None,
            'export_service': export_service is not None
        }
        
        # Database health
        try:
            health_query = "SELECT 1 as healthy"
            health_result = execute_query(health_query)
            stats['database_healthy'] = len(health_result) > 0
        except:
            stats['database_healthy'] = False
        
        return stats
    except Exception as e:
        return {"error": str(e), "status": "unhealthy"}

# =============================================================================
# RESOURCES
# =============================================================================

@mcp.resource("crosswalk://profiles/all")
def profiles_resource() -> str:
    """
    Resource exposing all source profiles with their metadata.
    
    Returns JSON list of all created source profiles.
    """
    try:
        profiles = list_profiles()
        return json.dumps(profiles, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.resource("crosswalk://pi20/fields")
def pi20_fields_resource() -> str:
    """
    Resource exposing all PI20 data model fields.
    
    Returns JSON list of all PI20 fields with their details.
    """
    try:
        fields = list_all_pi20_fields()
        return json.dumps(fields, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.resource("crosswalk://mappings/{profile_id}")
def profile_mappings_resource(profile_id: str) -> str:
    """
    Resource exposing crosswalk mappings for a specific profile.
    
    Args:
        profile_id: ID of the profile to get mappings for
    
    Returns JSON list of all mappings for the specified profile.
    """
    try:
        mappings = get_crosswalk_mappings(int(profile_id))
        return json.dumps(mappings, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.resource("crosswalk://system/stats")
def system_stats_resource() -> str:
    """
    Resource exposing system statistics and health information.
    
    Returns JSON object with comprehensive system stats.
    """
    try:
        stats = get_system_stats()
        return json.dumps(stats, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

# =============================================================================
# PROMPTS
# =============================================================================

@mcp.prompt()
def analyze_healthcare_data(data_description: str) -> str:
    """
    Generate a prompt for analyzing healthcare data and creating crosswalk mappings.
    
    Args:
        data_description: Description of the healthcare data to analyze
    """
    return f"""Please help me analyze this healthcare data and create appropriate crosswalk mappings to the PI20 data model:

{data_description}

Steps to follow:
1. Use `create_profile()` to create a new source profile for this data
2. Use `search_pi20_fields()` to find relevant PI20 fields for mapping
3. Use `suggest_mappings()` or `suggest_single_mapping()` to get AI-powered mapping suggestions
4. Use `create_crosswalk_mapping()` to establish the mappings
5. Use `export_crosswalk_json()` or `export_crosswalk_csv()` to export the results

Available resources:
- crosswalk://pi20/fields - All available PI20 fields
- crosswalk://profiles/all - All existing profiles
- crosswalk://system/stats - System health and statistics

Let me know if you need help with any specific step in the mapping process!"""

@mcp.prompt()
def troubleshoot_mapping_issues(issue_description: str) -> str:
    """
    Generate a prompt for troubleshooting mapping and data quality issues.
    
    Args:
        issue_description: Description of the mapping issue
    """
    return f"""I'll help you troubleshoot this mapping issue:

{issue_description}

Let me check the system status and provide recommendations:

1. First, let me run `get_system_stats()` to check overall system health
2. Then I'll examine the specific profiles and mappings involved
3. I'll look for common issues like:
   - Incorrect field names or data types
   - Missing source columns
   - Transformation logic errors
   - Data quality problems

Common solutions:
- Use `update_crosswalk_mapping()` to fix mapping errors
- Use `add_mapping_correction()` to improve future suggestions
- Use `search_pi20_fields()` to find alternative target fields
- Use `get_profile_details()` to verify source data structure

What specific aspect of the mapping would you like me to investigate first?"""

def main():
    """Main function to initialize and run the MCP server"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Initializing CrosswalkAI MCP Server...")
    
    # Check database connectivity
    try:
        stats = get_system_stats()
        if "error" not in stats:
            logger.info(f"✅ Database connected - {stats.get('pi20_fields', 0)} PI20 fields available")
        else:
            logger.warning(f"⚠️  Database issue: {stats.get('error', 'Unknown error')}")
    except Exception as e:
        logger.warning(f"⚠️  Could not check database status: {e}")
    
    # Log available services
    services_status = []
    if auto_mapper:
        services_status.append("✅ AutoMapper")
    else:
        services_status.append("❌ AutoMapper")
    
    if file_parser:
        services_status.append("✅ FileParser")
    else:
        services_status.append("❌ FileParser")
    
    if export_service:
        services_status.append("✅ ExportService")
    else:
        services_status.append("❌ ExportService")
    
    logger.info(f"📦 Services: {' | '.join(services_status)}")
    
    # Show available tools
    logger.info("🔧 Available tools: create_profile, search_pi20_fields, suggest_mappings, export_crosswalk_csv, and more...")
    
    try:
        logger.info("🌐 Starting MCP server on default port...")
        logger.info("📡 Server ready for MCP client connections!")
        logger.info("🛑 Press Ctrl+C to stop the server")
        
        # Run the MCP server
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        raise

if __name__ == "__main__":
    main()
