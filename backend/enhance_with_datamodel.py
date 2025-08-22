#!/usr/bin/env python3
"""
Enhance the database with data model intelligence from the PowerPoint training
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def enhance_with_datamodel():
    """Enhance database with data model structure and validation"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is required")
        sys.exit(1)
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🏗️  Enhancing database with data model intelligence...")
        
        # Create PI20 data model reference table
        print("Creating PI20 data model reference...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS pi20_data_model (
                id SERIAL PRIMARY KEY,
                schema_layer VARCHAR(20) NOT NULL, -- RAW, CLEANSE, CURATED
                table_name VARCHAR(100) NOT NULL,
                column_name VARCHAR(255) NOT NULL,
                data_type VARCHAR(100),
                description TEXT,
                is_standard_field BOOLEAN DEFAULT TRUE, -- FALSE for custom fields
                is_case_sensitive BOOLEAN DEFAULT FALSE, -- VARCHAR fields needing UPPER/LOWER
                source_layer VARCHAR(20), -- Which layer this field originates from
                join_logic TEXT, -- How to join to this table
                validation_rules TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(schema_layer, table_name, column_name)
            );
        """))
        
        # Insert PI20 data model structure based on PowerPoint
        print("Loading PI20 data model structure...")
        
        # CLAIM_HEADER table (CLEANSE and CURATED)
        claim_header_fields = [
            # Standard audit fields (all tables have these)
            ('BOTH', 'CLAIM_HEADER', 'DP_CREATE_TIMESTAMP', 'TIMESTAMP', 'Data pipeline create timestamp', True, False),
            ('BOTH', 'CLAIM_HEADER', 'DP_UPDATE_TIMESTAMP', 'TIMESTAMP', 'Data pipeline update timestamp', True, False),
            ('BOTH', 'CLAIM_HEADER', 'DP_RUN_ID', 'VARCHAR(50)', 'Data pipeline run identifier', True, False),
            
            # Core claim header fields
            ('BOTH', 'CLAIM_HEADER', 'CLAIM_HEADER_SID', 'BIGINT', 'Claim header surrogate key', True, False),
            ('BOTH', 'CLAIM_HEADER', 'CLAIM_ID', 'VARCHAR(50)', 'Unique claim identifier', True, True),
            ('BOTH', 'CLAIM_HEADER', 'MEMBER_SID', 'BIGINT', 'Member SID from claim file data', True, False),
            ('BOTH', 'CLAIM_HEADER', 'MEMBER_MBR_FILE_SID', 'BIGINT', 'Member SID from member file data', True, False),
            
            # Provider SIDs (multiple roles)
            ('BOTH', 'CLAIM_HEADER', 'PROVIDER_ATTENDING_SID', 'BIGINT', 'Attending provider SID from claim file', True, False),
            ('BOTH', 'CLAIM_HEADER', 'PROVIDER_ATTENDING_PROV_FILE_SID', 'BIGINT', 'Attending provider SID from provider file', True, False),
            ('BOTH', 'CLAIM_HEADER', 'PROVIDER_BILLING_SID', 'BIGINT', 'Billing provider SID from claim file', True, False),
            ('BOTH', 'CLAIM_HEADER', 'PROVIDER_BILLING_PROV_FILE_SID', 'BIGINT', 'Billing provider SID from provider file', True, False),
            
            # Diagnosis and procedure codes (now at header level)
            ('BOTH', 'CLAIM_HEADER', 'DIAGNOSIS_1', 'VARCHAR(20)', 'Primary diagnosis code', True, True),
            ('BOTH', 'CLAIM_HEADER', 'DIAGNOSIS_2', 'VARCHAR(20)', 'Secondary diagnosis code', True, True),
            ('BOTH', 'CLAIM_HEADER', 'PROCEDURE_1', 'VARCHAR(20)', 'Primary procedure code', True, True),
            ('BOTH', 'CLAIM_HEADER', 'PROCEDURE_2', 'VARCHAR(20)', 'Secondary procedure code', True, True),
            
            # Common claim fields
            ('BOTH', 'CLAIM_HEADER', 'SERVICE_FROM_DT', 'DATE', 'Service from date', True, False),
            ('BOTH', 'CLAIM_HEADER', 'SERVICE_TO_DT', 'DATE', 'Service to date', True, False),
            ('BOTH', 'CLAIM_HEADER', 'CLAIM_TYPE', 'VARCHAR(20)', 'Type of claim (MEDICAL, etc.)', True, True),
            ('BOTH', 'CLAIM_HEADER', 'CLAIM_STATUS', 'VARCHAR(20)', 'Claim processing status', True, True),
            
            # Custom field example (only in CLEANSE)
            ('CLEANSE', 'CLAIM_HEADER', 'STATEMENT_DT', 'DATE', 'Custom statement date field', False, False),
        ]
        
        # CLAIM_LINE table
        claim_line_fields = [
            ('BOTH', 'CLAIM_LINE', 'DP_CREATE_TIMESTAMP', 'TIMESTAMP', 'Data pipeline create timestamp', True, False),
            ('BOTH', 'CLAIM_LINE', 'DP_UPDATE_TIMESTAMP', 'TIMESTAMP', 'Data pipeline update timestamp', True, False),
            ('BOTH', 'CLAIM_LINE', 'DP_RUN_ID', 'VARCHAR(50)', 'Data pipeline run identifier', True, False),
            ('BOTH', 'CLAIM_LINE', 'CLAIM_LINE_SID', 'BIGINT', 'Claim line surrogate key', True, False),
            ('BOTH', 'CLAIM_LINE', 'CLAIM_HEADER_SID', 'BIGINT', 'Foreign key to claim header', True, False),
            ('BOTH', 'CLAIM_LINE', 'PROVIDER_RENDERING_SID', 'BIGINT', 'Rendering provider SID', True, False),
            ('BOTH', 'CLAIM_LINE', 'LINE_NUMBER', 'INTEGER', 'Claim line number', True, False),
            ('BOTH', 'CLAIM_LINE', 'PROCEDURE_CODE', 'VARCHAR(20)', 'Line-level procedure code', True, True),
            ('BOTH', 'CLAIM_LINE', 'ALLOWED_AMOUNT', 'DECIMAL(10,2)', 'Allowed amount', True, False),
            ('BOTH', 'CLAIM_LINE', 'PAID_AMOUNT', 'DECIMAL(10,2)', 'Paid amount', True, False),
            
            # CLAIM_LINE_AARETE only in CURATED
            ('CURATED', 'CLAIM_LINE_AARETE', 'CLAIM_LINE_SID', 'BIGINT', 'Join key to CLAIM_LINE table', True, False),
        ]
        
        # MEMBER table
        member_fields = [
            ('BOTH', 'MEMBER', 'DP_CREATE_TIMESTAMP', 'TIMESTAMP', 'Data pipeline create timestamp', True, False),
            ('BOTH', 'MEMBER', 'DP_UPDATE_TIMESTAMP', 'TIMESTAMP', 'Data pipeline update timestamp', True, False),
            ('BOTH', 'MEMBER', 'DP_RUN_ID', 'VARCHAR(50)', 'Data pipeline run identifier', True, False),
            ('BOTH', 'MEMBER', 'MEMBER_SID', 'BIGINT', 'Member surrogate key', True, False),
            ('BOTH', 'MEMBER', 'MEMBER_ID', 'VARCHAR(50)', 'Member identifier', True, True),
            ('BOTH', 'MEMBER', 'MBR_PRODUCT_LINE_OF_BUSINESS', 'VARCHAR(50)', 'Member line of business (case sensitive!)', True, True),
            ('BOTH', 'MEMBER', 'FIRST_NAME', 'VARCHAR(100)', 'Member first name', True, True),
            ('BOTH', 'MEMBER', 'LAST_NAME', 'VARCHAR(100)', 'Member last name', True, True),
            ('BOTH', 'MEMBER', 'DATE_OF_BIRTH', 'DATE', 'Member date of birth', True, False),
            ('BOTH', 'MEMBER', 'GENDER', 'VARCHAR(1)', 'Member gender', True, True),
        ]
        
        # PROVIDER table
        provider_fields = [
            ('BOTH', 'PROVIDER', 'DP_CREATE_TIMESTAMP', 'TIMESTAMP', 'Data pipeline create timestamp', True, False),
            ('BOTH', 'PROVIDER', 'DP_UPDATE_TIMESTAMP', 'TIMESTAMP', 'Data pipeline update timestamp', True, False),
            ('BOTH', 'PROVIDER', 'DP_RUN_ID', 'VARCHAR(50)', 'Data pipeline run identifier', True, False),
            ('BOTH', 'PROVIDER', 'PROVIDER_SID', 'BIGINT', 'Provider surrogate key', True, False),
            ('BOTH', 'PROVIDER', 'NPI', 'VARCHAR(10)', 'National Provider Identifier', True, False),
            ('BOTH', 'PROVIDER', 'PROVIDER_NAME', 'VARCHAR(255)', 'Provider name', True, True),
            ('BOTH', 'PROVIDER', 'TAXONOMY', 'VARCHAR(50)', 'Provider taxonomy code', True, True),
            ('BOTH', 'PROVIDER', 'SPECIALTY', 'VARCHAR(100)', 'Provider specialty', True, True),
        ]
        
        # Insert all data model fields
        all_fields = claim_header_fields + claim_line_fields + member_fields + provider_fields
        
        for layer, table, column, dtype, desc, is_standard, is_case_sensitive in all_fields:
            if layer == 'BOTH':
                # Insert for both CLEANSE and CURATED
                for schema_layer in ['CLEANSE', 'CURATED']:
                    try:
                        db.execute(text("""
                            INSERT INTO pi20_data_model 
                            (schema_layer, table_name, column_name, data_type, description, is_standard_field, is_case_sensitive)
                            VALUES (:schema_layer, :table_name, :column_name, :data_type, :description, :is_standard_field, :is_case_sensitive)
                            ON CONFLICT (schema_layer, table_name, column_name) DO NOTHING
                        """), {
                            'schema_layer': schema_layer,
                            'table_name': table,
                            'column_name': column,
                            'data_type': dtype,
                            'description': desc,
                            'is_standard_field': is_standard,
                            'is_case_sensitive': is_case_sensitive
                        })
                    except Exception as e:
                        print(f"Warning: Could not insert {schema_layer}.{table}.{column}: {e}")
            else:
                # Insert for specific layer only
                try:
                    db.execute(text("""
                        INSERT INTO pi20_data_model 
                        (schema_layer, table_name, column_name, data_type, description, is_standard_field, is_case_sensitive)
                        VALUES (:schema_layer, :table_name, :column_name, :data_type, :description, :is_standard_field, :is_case_sensitive)
                        ON CONFLICT (schema_layer, table_name, column_name) DO NOTHING
                    """), {
                        'schema_layer': layer,
                        'table_name': table,
                        'column_name': column,
                        'data_type': dtype,
                        'description': desc,
                        'is_standard_field': is_standard,
                        'is_case_sensitive': is_case_sensitive
                    })
                except Exception as e:
                    print(f"Warning: Could not insert {layer}.{table}.{column}: {e}")
        
        # Create validation rules table
        print("Creating validation rules...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS crosswalk_validation_rules (
                id SERIAL PRIMARY KEY,
                rule_name VARCHAR(100) NOT NULL,
                rule_type VARCHAR(50) NOT NULL, -- 'IN_MODEL_VALIDATION', 'VARCHAR_CASE_CHECK', 'DATA_TYPE_VALIDATION'
                rule_logic TEXT NOT NULL,
                error_message TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Insert common validation rules
        validation_rules = [
            ('IN_MODEL_Y_REQUIRES_MCDM_COLUMN', 'IN_MODEL_VALIDATION', 
             "in_model = 'Y' AND (mcdm_column_name IS NULL OR mcdm_column_name = '')", 
             'Fields with IN_MODEL=Y must have an MCDM column name specified'),
            
            ('VARCHAR_FIELDS_CASE_SENSITIVITY', 'VARCHAR_CASE_CHECK',
             "source_column_formatting IS NULL AND mcdm_column_name IN (SELECT column_name FROM pi20_data_model WHERE is_case_sensitive = TRUE)",
             'VARCHAR fields require UPPER() or LOWER() function in source formatting'),
            
            ('CUSTOM_FIELD_TYPE_VALIDATION', 'DATA_TYPE_VALIDATION',
             "in_model = 'N' AND custom_field_type IS NULL",
             'Custom fields (IN_MODEL=N) must specify a custom field type'),
             
            ('SKIPPED_FIELD_LOGIC', 'IN_MODEL_VALIDATION',
             "skipped_flag = TRUE AND in_model != 'N/A'",
             'Skipped fields should have IN_MODEL set to N/A'),
        ]
        
        for rule_name, rule_type, logic, message in validation_rules:
            try:
                db.execute(text("""
                    INSERT INTO crosswalk_validation_rules (rule_name, rule_type, rule_logic, error_message)
                    VALUES (:rule_name, :rule_type, :rule_logic, :error_message)
                    ON CONFLICT DO NOTHING
                """), {
                    'rule_name': rule_name,
                    'rule_type': rule_type,
                    'rule_logic': logic,
                    'error_message': message
                })
            except Exception as e:
                print(f"Warning: Could not insert validation rule {rule_name}: {e}")
        
        db.commit()
        
        # Show summary
        pi20_count = db.execute(text("SELECT COUNT(*) FROM pi20_data_model")).scalar()
        validation_count = db.execute(text("SELECT COUNT(*) FROM crosswalk_validation_rules")).scalar()
        
        print(f"✅ Enhanced database with PI20 data model intelligence!")
        print(f"📊 Added {pi20_count} data model fields")
        print(f"🔍 Added {validation_count} validation rules")
        print(f"🏗️  Data model structure: RAW → CLEANSE → CURATED layers")
        print(f"⚡ Ready for intelligent crosswalk validation and assistance!")
        
    except Exception as e:
        print(f"❌ Error enhancing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    enhance_with_datamodel()