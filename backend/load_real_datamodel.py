#!/usr/bin/env python3
"""
Load the real data model from Excel into the database
"""

import pandas as pd
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def load_real_datamodel():
    """Load the actual data model from Excel into database"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is required")
        sys.exit(1)
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Read the extracted data model
        if not os.path.exists("data_model_from_excel.csv"):
            print("❌ data_model_from_excel.csv not found. Run extract_datamodel_sheet.py first")
            return
        
        df = pd.read_csv("data_model_from_excel.csv")
        print(f"📊 Loading {len(df)} fields from Excel data model")
        
        # Clear existing data model
        print("🗑️  Clearing existing PI20 data model...")
        db.execute(text("DELETE FROM pi20_data_model"))
        
        # Insert real data model
        print("📥 Loading real data model...")
        inserted_count = 0
        
        for _, row in df.iterrows():
            table_name = str(row['TABLE_NAME']).strip()
            column_name = str(row['COLUMN_NAME']).strip()
            column_type = str(row['COLUMN_TYPE']).strip() if pd.notna(row['COLUMN_TYPE']) else 'VARCHAR'
            column_comment = str(row['COLUMN_COMMENT']).strip() if pd.notna(row['COLUMN_COMMENT']) else ''
            in_crosswalk = str(row['IN_CROSSWALK']).strip().upper() if pd.notna(row['IN_CROSSWALK']) else 'N'
            is_mandatory = bool(row['IS_MANDATORY']) if pd.notna(row['IS_MANDATORY']) else False
            
            # Skip empty rows
            if not table_name or table_name == 'nan' or not column_name or column_name == 'nan':
                continue
            
            # Determine schema layer (default to CURATED, but some might be CLEANSE-specific)
            schema_layer = 'CURATED'  # Most fields are in CURATED
            
            # Check if it's case sensitive (VARCHAR fields are usually case sensitive)
            is_case_sensitive = 'VARCHAR' in column_type.upper()
            
            # Determine if it's a standard field (most are standard)
            is_standard_field = in_crosswalk != 'Y'  # Fields not in crosswalk are typically standard/technical
            
            try:
                db.execute(text("""
                    INSERT INTO pi20_data_model 
                    (schema_layer, table_name, column_name, data_type, description, 
                     is_standard_field, is_case_sensitive, source_layer, validation_rules)
                    VALUES (:schema_layer, :table_name, :column_name, :data_type, :description,
                            :is_standard_field, :is_case_sensitive, :source_layer, :validation_rules)
                """), {
                    'schema_layer': schema_layer,
                    'table_name': table_name,
                    'column_name': column_name,
                    'data_type': column_type,
                    'description': column_comment,
                    'is_standard_field': is_standard_field,
                    'is_case_sensitive': is_case_sensitive,
                    'source_layer': 'EXCEL_DATA_MODEL',
                    'validation_rules': f"MANDATORY: {is_mandatory}, IN_CROSSWALK: {in_crosswalk}"
                })
                inserted_count += 1
                
            except Exception as e:
                print(f"Warning: Could not insert {table_name}.{column_name}: {e}")
        
        # Also add CLEANSE layer for custom fields (duplicating key tables)
        print("📥 Adding CLEANSE layer for custom fields...")
        cleanse_tables = ['CLAIM_HEADER', 'CLAIM_LINE', 'MEMBER', 'PROVIDER']
        
        for table in cleanse_tables:
            # Get all fields for this table from CURATED
            curated_fields = db.execute(text("""
                SELECT column_name, data_type, description, is_case_sensitive
                FROM pi20_data_model 
                WHERE table_name = :table AND schema_layer = 'CURATED'
            """), {'table': table}).fetchall()
            
            for field in curated_fields:
                try:
                    db.execute(text("""
                        INSERT INTO pi20_data_model 
                        (schema_layer, table_name, column_name, data_type, description, 
                         is_standard_field, is_case_sensitive, source_layer)
                        VALUES (:schema_layer, :table_name, :column_name, :data_type, :description,
                                :is_standard_field, :is_case_sensitive, :source_layer)
                    """), {
                        'schema_layer': 'CLEANSE',
                        'table_name': table,
                        'column_name': field[0],
                        'data_type': field[1],
                        'description': f"{field[2]} (CLEANSE layer - supports custom fields)",
                        'is_standard_field': True,
                        'is_case_sensitive': field[3],
                        'source_layer': 'EXCEL_DATA_MODEL_CLEANSE'
                    })
                except:
                    pass  # Skip duplicates
        
        db.commit()
        
        # Show summary
        total_count = db.execute(text("SELECT COUNT(*) FROM pi20_data_model")).scalar()
        table_count = db.execute(text("SELECT COUNT(DISTINCT table_name) FROM pi20_data_model")).scalar()
        
        print(f"✅ Loaded real data model!")
        print(f"📊 Inserted {inserted_count} fields from Excel")
        print(f"📊 Total fields in database: {total_count}")
        print(f"🏢 Tables covered: {table_count}")
        print(f"🏗️  Schema layers: CURATED (from Excel) + CLEANSE (with custom fields)")
        
        # Show table breakdown
        print(f"\n📋 Table breakdown:")
        table_counts = db.execute(text("""
            SELECT table_name, COUNT(*) as field_count
            FROM pi20_data_model 
            WHERE schema_layer = 'CURATED'
            GROUP BY table_name 
            ORDER BY field_count DESC
        """)).fetchall()
        
        for table_name, count in table_counts:
            print(f"  {table_name}: {count} fields")
        
    except Exception as e:
        print(f"❌ Error loading data model: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_real_datamodel()