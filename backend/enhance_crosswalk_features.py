#!/usr/bin/env python3
"""
Enhance crosswalk with the 8 real-world features requested
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def enhance_crosswalk_features():
    """Add all the requested features to the crosswalk system"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is required")
        sys.exit(1)
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🚀 Enhancing crosswalk with 8 real-world features...")
        
        # Feature 1 & 2: Multi-table assignment and FILE_GROUP for providers
        print("1️⃣ Adding multi-table support and FILE_GROUP...")
        db.execute(text("""
            ALTER TABLE crosswalk_template 
            ADD COLUMN IF NOT EXISTS target_tables TEXT, -- JSON array for multiple tables
            ADD COLUMN IF NOT EXISTS provider_file_group VARCHAR(50), -- BILLING, RENDERING, etc.
            ADD COLUMN IF NOT EXISTS is_multi_table BOOLEAN DEFAULT FALSE
        """))
        
        # Feature 3: Version control and reuse
        print("3️⃣ Adding version control and reuse functionality...")
        db.execute(text("""
            ALTER TABLE crosswalk_template 
            ADD COLUMN IF NOT EXISTS crosswalk_version VARCHAR(20) DEFAULT '1.0',
            ADD COLUMN IF NOT EXISTS parent_mapping_id INTEGER, -- Reference to original mapping
            ADD COLUMN IF NOT EXISTS reuse_from_client VARCHAR(50), -- Reuse from another client
            ADD COLUMN IF NOT EXISTS version_notes TEXT
        """))
        
        # Feature 4: Data type inference
        print("4️⃣ Adding data type inference...")
        db.execute(text("""
            ALTER TABLE crosswalk_template 
            ADD COLUMN IF NOT EXISTS inferred_data_type VARCHAR(100), -- From data model
            ADD COLUMN IF NOT EXISTS custom_data_type VARCHAR(100), -- Manual override
            ADD COLUMN IF NOT EXISTS data_type_source VARCHAR(20) DEFAULT 'INFERRED' -- INFERRED, MANUAL, UNKNOWN
        """))
        
        # Feature 5: Multiple file joins
        print("5️⃣ Adding multi-file join support...")
        db.execute(text("""
            ALTER TABLE crosswalk_template 
            ADD COLUMN IF NOT EXISTS source_file_name VARCHAR(255), -- Which source file this comes from
            ADD COLUMN IF NOT EXISTS join_key_column VARCHAR(255), -- _SID column for joining
            ADD COLUMN IF NOT EXISTS join_table VARCHAR(100), -- Table to join to
            ADD COLUMN IF NOT EXISTS join_type VARCHAR(20) DEFAULT 'INNER' -- INNER, LEFT, etc.
        """))
        
        # Feature 7: MCS review flags
        print("7️⃣ Adding MCS review flags...")
        db.execute(text("""
            ALTER TABLE crosswalk_template 
            ADD COLUMN IF NOT EXISTS mcs_review_required BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS mcs_review_notes TEXT,
            ADD COLUMN IF NOT EXISTS mcs_review_status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, IN_REVIEW, APPROVED, REJECTED
            ADD COLUMN IF NOT EXISTS mcs_reviewer VARCHAR(100),
            ADD COLUMN IF NOT EXISTS mcs_review_date TIMESTAMP
        """))
        
        # Additional tracking fields
        print("📊 Adding enhanced tracking...")
        db.execute(text("""
            ALTER TABLE crosswalk_template 
            ADD COLUMN IF NOT EXISTS complexity_score INTEGER DEFAULT 1, -- 1-5 complexity rating
            ADD COLUMN IF NOT EXISTS business_priority VARCHAR(20) DEFAULT 'MEDIUM', -- HIGH, MEDIUM, LOW
            ADD COLUMN IF NOT EXISTS completion_status VARCHAR(20) DEFAULT 'DRAFT' -- DRAFT, READY, VALIDATED, DEPLOYED
        """))
        
        # Feature 6: Create table for Snowflake SQL generation tracking
        print("6️⃣ Creating Snowflake SQL generation tracking...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS snowflake_sql_exports (
                id SERIAL PRIMARY KEY,
                client_id VARCHAR(50) NOT NULL,
                file_group VARCHAR(100),
                export_type VARCHAR(20) NOT NULL, -- CREATE_TABLE, INSERT_MAPPING, FULL_ETL
                sql_content TEXT,
                table_name VARCHAR(100),
                created_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deployed BOOLEAN DEFAULT FALSE,
                deployment_notes TEXT
            )
        """))
        
        # Create indexes for better performance
        print("⚡ Creating performance indexes...")
        try:
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_crosswalk_completion_status ON crosswalk_template(completion_status)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_crosswalk_mcs_review ON crosswalk_template(mcs_review_required, mcs_review_status)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_crosswalk_version ON crosswalk_template(crosswalk_version, client_id)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_crosswalk_multi_table ON crosswalk_template(is_multi_table)"))
        except:
            pass  # Indexes might already exist
        
        # Update existing records with smart defaults
        print("🔄 Updating existing records with smart defaults...")
        
        # Infer data types from data model
        db.execute(text("""
            UPDATE crosswalk_template ct
            SET inferred_data_type = dm.data_type,
                data_type_source = 'INFERRED'
            FROM pi20_data_model dm
            WHERE ct.mcdm_column_name = dm.column_name
            AND ct.inferred_data_type IS NULL
        """))
        
        # Set completion status based on current state
        db.execute(text("""
            UPDATE crosswalk_template 
            SET completion_status = CASE 
                WHEN skipped_flag = TRUE THEN 'SKIPPED'
                WHEN in_model = 'Y' AND mcdm_column_name IS NOT NULL AND mcdm_column_name != '' THEN 'READY'
                WHEN in_model = 'Y' AND (mcdm_column_name IS NULL OR mcdm_column_name = '') THEN 'DRAFT'
                WHEN in_model = 'N' THEN 'CUSTOM'
                ELSE 'DRAFT'
            END
            WHERE completion_status = 'DRAFT'
        """))
        
        # Flag complex provider fields for MCS review
        db.execute(text("""
            UPDATE crosswalk_template 
            SET mcs_review_required = TRUE,
                mcs_review_notes = 'Provider field - needs FILE_GROUP specification'
            WHERE file_group_name = 'PROVIDER' 
            AND provider_file_group IS NULL
        """))
        
        # Flag multi-table scenarios for MCS review  
        db.execute(text("""
            UPDATE crosswalk_template 
            SET mcs_review_required = TRUE,
                mcs_review_notes = 'Potential multi-table field - verify target tables',
                is_multi_table = TRUE
            WHERE (source_column_name ILIKE '%claim%' OR source_column_name ILIKE '%header%' OR source_column_name ILIKE '%line%')
            AND file_group_name IN ('CLAIM', 'CLAIM_LINE')
        """))
        
        db.commit()
        
        # Show summary of enhancements
        total_mappings = db.execute(text("SELECT COUNT(*) FROM crosswalk_template")).scalar()
        mcs_review_count = db.execute(text("SELECT COUNT(*) FROM crosswalk_template WHERE mcs_review_required = TRUE")).scalar()
        multi_table_count = db.execute(text("SELECT COUNT(*) FROM crosswalk_template WHERE is_multi_table = TRUE")).scalar()
        inferred_types = db.execute(text("SELECT COUNT(*) FROM crosswalk_template WHERE data_type_source = 'INFERRED'")).scalar()
        
        print(f"\n✅ Enhanced crosswalk system with 8 real-world features!")
        print(f"📊 Total mappings: {total_mappings}")
        print(f"🔍 MCS review required: {mcs_review_count}")
        print(f"🔗 Multi-table fields: {multi_table_count}")
        print(f"🎯 Data types inferred: {inferred_types}")
        print(f"")
        print(f"🚀 Features implemented:")
        print(f"  1️⃣ Multi-table assignment (claim_line + claim_header)")
        print(f"  2️⃣ Provider FILE_GROUP flags")
        print(f"  3️⃣ Version control and reuse")
        print(f"  4️⃣ Data type inference from data model")
        print(f"  5️⃣ Multi-file join support (_SID columns)")
        print(f"  6️⃣ Snowflake SQL generation tracking")
        print(f"  7️⃣ MCS team review flags")
        print(f"  8️⃣ Enhanced filtering capabilities")
        
    except Exception as e:
        print(f"❌ Error enhancing crosswalk: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    enhance_crosswalk_features()