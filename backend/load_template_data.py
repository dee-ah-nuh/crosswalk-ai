#!/usr/bin/env python3
"""
Load data from the Excel crosswalk template into the database
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def load_template_data():
    """Load data from the crosswalk template Excel file"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is required")
        sys.exit(1)
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("📊 Loading data from crosswalk template...")
        
        # Load the Medical sheet
        excel_file = "../attached_assets/CLIENT_GDP_Crosswalk_1755826997501.xlsx"
        print(f"Reading Excel file: {excel_file}")
        
        df = pd.read_excel(excel_file, sheet_name='Medical', header=0)
        print(f"Loaded {len(df)} rows from Medical sheet")
        
        # Clean up the data and prepare for insertion
        successful_inserts = 0
        
        for index, row in df.iterrows():
            if index < 2:  # Skip first 2 rows (headers and formulas)
                continue
                
            # Skip empty rows
            if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                continue
                
            try:
                # Map Excel columns to database fields
                client_id = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                source_column_order = int(row.iloc[1]) if pd.notna(row.iloc[1]) and str(row.iloc[1]).isdigit() else None
                source_column_name = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
                file_group_name = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ''
                mcdm_column_name = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ''
                
                in_model = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else 'Y'
                mcdm_table = str(row.iloc[6]).strip() if pd.notna(row.iloc[6]) else ''
                custom_field_type = str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) else ''
                
                # Profile data columns (9-14)
                data_profile_info = str(row.iloc[8]).strip() if pd.notna(row.iloc[8]) else ''
                profile_col_2 = str(row.iloc[9]).strip() if pd.notna(row.iloc[9]) else ''
                profile_col_3 = str(row.iloc[10]).strip() if pd.notna(row.iloc[10]) else ''
                profile_col_4 = str(row.iloc[11]).strip() if pd.notna(row.iloc[11]) else ''
                profile_col_5 = str(row.iloc[12]).strip() if pd.notna(row.iloc[12]) else ''
                profile_col_6 = str(row.iloc[13]).strip() if pd.notna(row.iloc[13]) else ''
                
                source_column_formatting = str(row.iloc[14]).strip() if pd.notna(row.iloc[14]) else ''
                skipped_flag = str(row.iloc[15]).strip().upper() == 'TRUE' if pd.notna(row.iloc[15]) else False
                
                # Additional fields for remaining columns
                additional_fields = []
                for i in range(16, min(len(row), 24)):  # Columns 17-24
                    additional_fields.append(str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else '')
                
                # Skip if essential fields are missing
                if not client_id or not source_column_name or not file_group_name:
                    continue
                
                # Insert into database
                insert_sql = text("""
                    INSERT INTO crosswalk_template (
                        client_id, source_column_order, source_column_name, file_group_name, mcdm_column_name,
                        in_model, mcdm_table, custom_field_type, data_profile_info,
                        profile_column_2, profile_column_3, profile_column_4, profile_column_5, profile_column_6,
                        source_column_formatting, skipped_flag,
                        additional_field_1, additional_field_2, additional_field_3, additional_field_4,
                        additional_field_5, additional_field_6, additional_field_7, additional_field_8
                    ) VALUES (
                        :client_id, :source_column_order, :source_column_name, :file_group_name, :mcdm_column_name,
                        :in_model, :mcdm_table, :custom_field_type, :data_profile_info,
                        :profile_column_2, :profile_column_3, :profile_column_4, :profile_column_5, :profile_column_6,
                        :source_column_formatting, :skipped_flag,
                        :additional_field_1, :additional_field_2, :additional_field_3, :additional_field_4,
                        :additional_field_5, :additional_field_6, :additional_field_7, :additional_field_8
                    )
                """)
                
                db.execute(insert_sql, {
                    'client_id': client_id,
                    'source_column_order': source_column_order,
                    'source_column_name': source_column_name,
                    'file_group_name': file_group_name,
                    'mcdm_column_name': mcdm_column_name,
                    'in_model': in_model,
                    'mcdm_table': mcdm_table,
                    'custom_field_type': custom_field_type,
                    'data_profile_info': data_profile_info,
                    'profile_column_2': profile_col_2,
                    'profile_column_3': profile_col_3,
                    'profile_column_4': profile_col_4,
                    'profile_column_5': profile_col_5,
                    'profile_column_6': profile_col_6,
                    'source_column_formatting': source_column_formatting,
                    'skipped_flag': skipped_flag,
                    'additional_field_1': additional_fields[0] if len(additional_fields) > 0 else '',
                    'additional_field_2': additional_fields[1] if len(additional_fields) > 1 else '',
                    'additional_field_3': additional_fields[2] if len(additional_fields) > 2 else '',
                    'additional_field_4': additional_fields[3] if len(additional_fields) > 3 else '',
                    'additional_field_5': additional_fields[4] if len(additional_fields) > 4 else '',
                    'additional_field_6': additional_fields[5] if len(additional_fields) > 5 else '',
                    'additional_field_7': additional_fields[6] if len(additional_fields) > 6 else '',
                    'additional_field_8': additional_fields[7] if len(additional_fields) > 7 else ''
                })
                successful_inserts += 1
                
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                continue
        
        # Create a sample client profile
        print("Creating sample client profiles...")
        
        # Get unique client/file_group combinations
        client_profiles = db.execute(text("""
            SELECT DISTINCT client_id, file_group_name 
            FROM crosswalk_template 
            WHERE client_id IS NOT NULL AND file_group_name IS NOT NULL
        """)).fetchall()
        
        for profile in client_profiles:
            client_id, file_group = profile
            try:
                db.execute(text("""
                    INSERT INTO client_profiles (client_id, client_name, file_group_name, version, description)
                    VALUES (:client_id, :client_name, :file_group_name, 'V00', 'Loaded from Excel template')
                    ON CONFLICT (client_id, file_group_name, version) DO NOTHING
                """), {
                    'client_id': client_id,
                    'client_name': f'{client_id} Client',
                    'file_group_name': file_group
                })
            except Exception as e:
                print(f"Error creating profile for {client_id}-{file_group}: {e}")
        
        db.commit()
        print(f"✅ Successfully loaded {successful_inserts} crosswalk mappings!")
        
        # Show summary
        total_mappings = db.execute(text("SELECT COUNT(*) FROM crosswalk_template")).scalar()
        total_profiles = db.execute(text("SELECT COUNT(*) FROM client_profiles")).scalar()
        
        print(f"📊 Database Summary:")
        print(f"   - Total crosswalk mappings: {total_mappings}")
        print(f"   - Total client profiles: {total_profiles}")
        
    except Exception as e:
        print(f"❌ Error loading template data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_template_data()