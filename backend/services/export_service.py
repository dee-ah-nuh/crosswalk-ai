"""
Export service for generating various output formats.
"""

import json
import csv
from io import StringIO, BytesIO
from typing import List, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session

from models import SourceProfile, SourceColumn, CrosswalkMapping, RegexRule, DataModelField
from services.dsl_engine import DSLEngine

class ExportService:
    """Service for exporting crosswalk data in various formats"""
    
    @staticmethod
    def export_crosswalk_csv(db: Session, profile_id: int) -> str:
        """Export crosswalk as CSV string"""
        profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
        if not profile:
            raise ValueError("Profile not found")
        
        # Get all mappings with related data
        mappings = db.query(CrosswalkMapping).filter(
            CrosswalkMapping.profile_id == profile_id
        ).all()
        
        # Prepare CSV data
        csv_data = []
        for mapping in mappings:
            source_column = db.query(SourceColumn).filter(
                SourceColumn.id == mapping.source_column_id
            ).first()
            
            regex_rules = db.query(RegexRule).filter(
                RegexRule.source_column_id == mapping.source_column_id
            ).all()
            
            csv_data.append({
                'client_id': profile.client_id or '',
                'source_column': source_column.source_column if source_column else '',
                'model_table': mapping.model_table,
                'model_column': mapping.model_column,
                'is_custom_field': mapping.is_custom_field,
                'custom_field_name': mapping.custom_field_name or '',
                'transform_expression': mapping.transform_expression or '',
                'regex_rules': json.dumps([{
                    'name': rule.rule_name,
                    'pattern': rule.pattern,
                    'flags': rule.flags,
                    'description': rule.description
                } for rule in regex_rules]),
                'notes': mapping.notes or ''
            })
        
        # Convert to CSV
        if not csv_data:
            return "client_id,source_column,model_table,model_column,is_custom_field,custom_field_name,transform_expression,regex_rules,notes\n"
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=csv_data[0].keys())
        writer.writeheader()
        writer.writerows(csv_data)
        return output.getvalue()
    
    @staticmethod
    def export_crosswalk_excel(db: Session, profile_id: int) -> bytes:
        """Export crosswalk as Excel bytes"""
        csv_content = ExportService.export_crosswalk_csv(db, profile_id)
        
        # Convert CSV to DataFrame and then to Excel
        df = pd.read_csv(StringIO(csv_content))
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Crosswalk', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    @staticmethod
    def export_json_config(db: Session, profile_id: int) -> Dict[str, Any]:
        """Export crosswalk as JSON configuration"""
        profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
        if not profile:
            raise ValueError("Profile not found")
        
        mappings = db.query(CrosswalkMapping).filter(
            CrosswalkMapping.profile_id == profile_id
        ).all()
        
        json_mappings = []
        for mapping in mappings:
            source_column = db.query(SourceColumn).filter(
                SourceColumn.id == mapping.source_column_id
            ).first()
            
            regex_rules = db.query(RegexRule).filter(
                RegexRule.source_column_id == mapping.source_column_id
            ).all()
            
            mapping_data = {
                "source_column": source_column.source_column if source_column else "",
                "target": {
                    "table": mapping.model_table,
                    "column": mapping.model_column
                },
                "custom": mapping.is_custom_field,
                "transform": mapping.transform_expression or "",
                "regex_rules": [{
                    "name": rule.rule_name,
                    "pattern": rule.pattern,
                    "flags": rule.flags,
                    "description": rule.description
                } for rule in regex_rules]
            }
            
            if mapping.is_custom_field:
                mapping_data["custom_field_name"] = mapping.custom_field_name
            
            json_mappings.append(mapping_data)
        
        return {
            "client_id": profile.client_id or "",
            "profile": profile.name,
            "mappings": json_mappings
        }
    
    @staticmethod
    def export_sql_script(db: Session, profile_id: int) -> str:
        """Export crosswalk as SQL script"""
        profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
        if not profile:
            raise ValueError("Profile not found")
        
        mappings = db.query(CrosswalkMapping).filter(
            CrosswalkMapping.profile_id == profile_id
        ).all()
        
        sql_lines = []
        
        # Create table DDL
        sql_lines.append("-- Crosswalk table creation (idempotent)")
        sql_lines.append("CREATE TABLE IF NOT EXISTS crosswalk_mappings (")
        sql_lines.append("    id INTEGER PRIMARY KEY,")
        sql_lines.append("    client_id VARCHAR(50),")
        sql_lines.append("    source_column VARCHAR(255),")
        sql_lines.append("    model_table VARCHAR(100),")
        sql_lines.append("    model_column VARCHAR(100),")
        sql_lines.append("    is_custom_field BOOLEAN DEFAULT FALSE,")
        sql_lines.append("    custom_field_name VARCHAR(255),")
        sql_lines.append("    transform_expression TEXT,")
        sql_lines.append("    regex_json TEXT,")
        sql_lines.append("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,")
        sql_lines.append("    UNIQUE(client_id, source_column)")
        sql_lines.append(");")
        sql_lines.append("")
        
        # Insert/Update statements
        sql_lines.append("-- Upsert crosswalk mappings")
        
        for mapping in mappings:
            source_column = db.query(SourceColumn).filter(
                SourceColumn.id == mapping.source_column_id
            ).first()
            
            regex_rules = db.query(RegexRule).filter(
                RegexRule.source_column_id == mapping.source_column_id
            ).all()
            
            regex_json = json.dumps([{
                'name': rule.rule_name,
                'pattern': rule.pattern,
                'flags': rule.flags,
                'description': rule.description
            } for rule in regex_rules])
            
            client_id = profile.client_id or 'DEFAULT'
            source_col = source_column.source_column if source_column else ''
            
            sql_lines.append(f"INSERT OR REPLACE INTO crosswalk_mappings (")
            sql_lines.append(f"    client_id, source_column, model_table, model_column,")
            sql_lines.append(f"    is_custom_field, custom_field_name, transform_expression, regex_json")
            sql_lines.append(f") VALUES (")
            sql_lines.append(f"    '{client_id}',")
            sql_lines.append(f"    '{source_col}',")
            sql_lines.append(f"    '{mapping.model_table}',")
            sql_lines.append(f"    '{mapping.model_column}',")
            sql_lines.append(f"    {1 if mapping.is_custom_field else 0},")
            sql_lines.append(f"    '{mapping.custom_field_name or ''}',")
            sql_lines.append(f"    '{mapping.transform_expression or ''}',")
            sql_lines.append(f"    '{regex_json}'")
            sql_lines.append(f");")
            sql_lines.append("")
        
        # Generate transformation view
        sql_lines.append("-- Example transformation view")
        sql_lines.append(f"CREATE OR REPLACE VIEW {profile.client_id or 'client'}_transformed AS")
        sql_lines.append("SELECT")
        
        select_clauses = []
        for mapping in mappings:
            source_column = db.query(SourceColumn).filter(
                SourceColumn.id == mapping.source_column_id
            ).first()
            
            if source_column and mapping.transform_expression:
                # Translate DSL to SQL
                sql_expr = DSLEngine.translate_to_sql(mapping.transform_expression)
                target_col = mapping.custom_field_name if mapping.is_custom_field else mapping.model_column
                select_clauses.append(f"    {sql_expr} AS {target_col}")
            elif source_column:
                target_col = mapping.custom_field_name if mapping.is_custom_field else mapping.model_column
                select_clauses.append(f"    {source_column.source_column} AS {target_col}")
        
        if select_clauses:
            sql_lines.append(",\n".join(select_clauses))
        else:
            sql_lines.append("    *")
        
        sql_lines.append(f"FROM {profile.raw_table_name or 'source_table'};")
        
        return "\n".join(sql_lines)
