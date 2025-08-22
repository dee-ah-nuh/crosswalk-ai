#!/usr/bin/env python3
"""
Update database schema to match the actual crosswalk template structure
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def update_schema():
    """Update the database schema to match the crosswalk template"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is required")
        sys.exit(1)
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🔄 Updating database schema to match crosswalk template...")
        
        # Drop existing tables to start fresh
        print("Dropping existing tables...")
        db.execute(text("""
            DROP TABLE IF EXISTS crosswalk_mappings CASCADE;
            DROP TABLE IF EXISTS source_columns CASCADE;
            DROP TABLE IF EXISTS source_profiles CASCADE;
            DROP TABLE IF EXISTS data_model_fields CASCADE;
            DROP TABLE IF EXISTS regex_rules CASCADE;
            DROP TABLE IF EXISTS warehouse_configs CASCADE;
        """))
        
        # Create crosswalk_template table matching the Excel structure
        print("Creating crosswalk_template table...")
        db.execute(text("""
            CREATE TABLE crosswalk_template (
                id SERIAL PRIMARY KEY,
                
                -- Core identification fields
                client_id VARCHAR(100) NOT NULL,
                source_column_order INTEGER,
                source_column_name VARCHAR(255) NOT NULL,
                file_group_name VARCHAR(100) NOT NULL, -- CLAIM, CLAIM_LINE, MEMBER, PROVIDER
                mcdm_column_name VARCHAR(255),
                
                -- Data flow control
                in_model VARCHAR(10) DEFAULT 'Y', -- Y, N, U, N/A
                mcdm_table VARCHAR(100),
                custom_field_type VARCHAR(50),
                
                -- Data profiling (calculated fields from Profile sheet)
                data_profile_info TEXT,
                profile_column_2 TEXT,
                profile_column_3 TEXT,
                profile_column_4 TEXT,
                profile_column_5 TEXT,
                profile_column_6 TEXT,
                
                -- Transformation and formatting
                source_column_formatting TEXT,
                skipped_flag BOOLEAN DEFAULT FALSE,
                
                -- Additional metadata fields from remaining columns
                additional_field_1 TEXT,
                additional_field_2 TEXT,
                additional_field_3 TEXT,
                additional_field_4 TEXT,
                additional_field_5 TEXT,
                additional_field_6 TEXT,
                additional_field_7 TEXT,
                additional_field_8 TEXT,
                
                -- Tracking
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create profiles table for client configurations
        print("Creating client_profiles table...")
        db.execute(text("""
            CREATE TABLE client_profiles (
                id SERIAL PRIMARY KEY,
                client_id VARCHAR(100) NOT NULL,
                client_name VARCHAR(255) NOT NULL,
                file_group_name VARCHAR(100) NOT NULL,
                version VARCHAR(50) DEFAULT 'V00',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(client_id, file_group_name, version)
            );
        """))
        
        # Create data_model_reference table (from your Data Model sheet)
        print("Creating data_model_reference table...")
        db.execute(text("""
            CREATE TABLE data_model_reference (
                id SERIAL PRIMARY KEY,
                table_name VARCHAR(100) NOT NULL,
                column_name VARCHAR(255) NOT NULL,
                data_type VARCHAR(100),
                description TEXT,
                is_required BOOLEAN DEFAULT FALSE,
                is_unique_key BOOLEAN DEFAULT FALSE,
                default_value TEXT,
                validation_rules TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(table_name, column_name)
            );
        """))
        
        # Create profile_data table (matches your Profile sheet lookups)
        print("Creating profile_data table...")
        db.execute(text("""
            CREATE TABLE profile_data (
                id SERIAL PRIMARY KEY,
                lookup_key VARCHAR(500) NOT NULL, -- Format: CLIENT_ID-FILE_GROUP_NAME-VERSION-COLUMN_NAME
                client_id VARCHAR(100) NOT NULL,
                file_group_name VARCHAR(100) NOT NULL,
                version VARCHAR(50) NOT NULL,
                column_name VARCHAR(255) NOT NULL,
                data_profile TEXT,
                profile_value_1 TEXT,
                profile_value_2 TEXT,
                profile_value_3 TEXT,
                profile_value_4 TEXT,
                profile_value_5 TEXT,
                sample_values TEXT, -- JSON array of sample values
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(lookup_key)
            );
        """))
        
        # Add indexes for performance
        print("Creating indexes...")
        db.execute(text("""
            CREATE INDEX idx_crosswalk_client_id ON crosswalk_template(client_id);
            CREATE INDEX idx_crosswalk_file_group ON crosswalk_template(file_group_name);
            CREATE INDEX idx_crosswalk_source_name ON crosswalk_template(source_column_name);
            CREATE INDEX idx_profile_lookup ON profile_data(lookup_key);
            CREATE INDEX idx_data_model_lookup ON data_model_reference(table_name, column_name);
        """))
        
        db.commit()
        print("✅ Database schema updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_schema()