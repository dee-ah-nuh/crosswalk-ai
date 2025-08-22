#!/usr/bin/env python3
"""
De-identify data by changing client to TEST and replacing real data with dummy data
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import random

def de_identify_data():
    """Replace real client data with de-identified dummy data"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is required")
        sys.exit(1)
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🛡️  De-identifying data - replacing with dummy data...")
        
        # Change client from UPHP to TEST
        print("1️⃣ Changing client ID to TEST...")
        db.execute(text("UPDATE crosswalk_template SET client_id = 'TEST' WHERE client_id = 'UPHP'"))
        
        # Get all current records to update with dummy data
        mappings = db.execute(text("SELECT id, source_column_name FROM crosswalk_template")).fetchall()
        
        print("2️⃣ Replacing real data profiles with dummy data...")
        
        # Sample dummy data profiles for different types of fields
        dummy_profiles = [
            "Sample text data: ABC123, DEF456, GHI789",
            "Numeric values: 100, 200, 300, 400, 500",
            "Date examples: 2024-01-15, 2024-02-20, 2024-03-10",
            "Boolean flags: Y, N, Y, Y, N",
            "ID patterns: 12345, 67890, 11111, 22222",
            "Amount data: $1000.00, $2500.50, $750.25",
            "Code values: A1B2, C3D4, E5F6, G7H8",
            "Status flags: ACTIVE, PENDING, CLOSED",
            "Category data: TYPE1, TYPE2, TYPE3",
            "Reference numbers: REF001, REF002, REF003"
        ]
        
        # Additional dummy profile columns
        dummy_columns = [
            "Sample additional field A",
            "Sample additional field B", 
            "Sample additional field C",
            "Sample additional field D",
            "Sample additional field E",
            "Sample additional field F"
        ]
        
        # Dummy source column names for different file groups
        claim_columns = [
            "claim_id", "claim_number", "patient_id", "provider_id", "claim_date",
            "service_date", "diagnosis_code", "procedure_code", "claim_amount",
            "copay_amount", "deductible", "claim_status", "auth_number",
            "member_id", "group_number", "plan_code", "service_type",
            "place_of_service", "rendering_provider", "billing_provider"
        ]
        
        member_columns = [
            "member_id", "first_name", "last_name", "date_of_birth", "gender",
            "address_line1", "city", "state", "zip_code", "phone_number",
            "email", "enrollment_date", "termination_date", "plan_id",
            "group_id", "employer_id", "relationship_code"
        ]
        
        provider_columns = [
            "provider_id", "provider_name", "npi_number", "tax_id", "specialty",
            "address_line1", "city", "state", "zip_code", "phone_number",
            "contract_date", "provider_type", "status", "network_indicator"
        ]
        
        # Update each mapping with dummy data
        for i, (mapping_id, current_source_col) in enumerate(mappings):
            # Determine file group and pick appropriate dummy column name
            if i < 280:  # Most records are claims
                new_source_col = random.choice(claim_columns) + f"_{i%20 + 1}"
                file_group = "CLAIM"
            elif i < 300:  # Some member records
                new_source_col = random.choice(member_columns) + f"_{i%10 + 1}" 
                file_group = "MEMBER"
            else:  # Provider records
                new_source_col = random.choice(provider_columns) + f"_{i%10 + 1}"
                file_group = "PROVIDER"
            
            # Pick random dummy profile data
            dummy_profile = random.choice(dummy_profiles)
            dummy_col_2 = random.choice(dummy_columns)
            dummy_col_3 = random.choice(dummy_columns)
            dummy_col_4 = random.choice(dummy_columns)
            dummy_col_5 = random.choice(dummy_columns)
            dummy_col_6 = random.choice(dummy_columns)
            
            # Update the record with dummy data
            db.execute(text("""
                UPDATE crosswalk_template 
                SET 
                    source_column_name = :new_source_col,
                    file_group_name = :file_group,
                    data_profile_info = :dummy_profile,
                    profile_column_2 = :dummy_col_2,
                    profile_column_3 = :dummy_col_3,
                    profile_column_4 = :dummy_col_4,
                    profile_column_5 = :dummy_col_5,
                    profile_column_6 = :dummy_col_6
                WHERE id = :mapping_id
            """), {
                'new_source_col': new_source_col,
                'file_group': file_group,
                'dummy_profile': dummy_profile,
                'dummy_col_2': dummy_col_2,
                'dummy_col_3': dummy_col_3,
                'dummy_col_4': dummy_col_4,
                'dummy_col_5': dummy_col_5,
                'dummy_col_6': dummy_col_6,
                'mapping_id': mapping_id
            })
        
        print("3️⃣ Updating additional fields with dummy data...")
        
        # Update additional fields with generic dummy values
        dummy_additional_fields = [
            "Sample field 1", "Sample field 2", "Sample field 3", 
            "Sample field 4", "Sample field 5", "Sample field 6",
            "Sample field 7", "Sample field 8"
        ]
        
        for i in range(8):
            field_name = f"additional_field_{i+1}"
            dummy_value = dummy_additional_fields[i]
            
            db.execute(text(f"""
                UPDATE crosswalk_template 
                SET {field_name} = :dummy_value 
                WHERE {field_name} IS NOT NULL
            """), {'dummy_value': dummy_value})
        
        print("4️⃣ Clearing any remaining sensitive data...")
        
        # Clear any potentially sensitive formatting or custom fields
        db.execute(text("""
            UPDATE crosswalk_template 
            SET 
                source_column_formatting = CASE 
                    WHEN source_column_formatting IS NOT NULL THEN 'TRIM(UPPER({source_column}))'
                    ELSE NULL 
                END,
                custom_field_type = CASE 
                    WHEN custom_field_type IS NOT NULL THEN 'CUSTOM_TYPE'
                    ELSE NULL 
                END,
                provider_file_group = CASE 
                    WHEN provider_file_group IS NOT NULL THEN 'BILLING'
                    ELSE NULL 
                END,
                version_notes = CASE 
                    WHEN version_notes IS NOT NULL THEN 'Sample version notes'
                    ELSE NULL 
                END,
                mcs_review_notes = CASE 
                    WHEN mcs_review_notes IS NOT NULL THEN 'Sample MCS review notes'
                    ELSE NULL 
                END
        """))
        
        db.commit()
        
        # Show summary
        total_updated = db.execute(text("SELECT COUNT(*) FROM crosswalk_template WHERE client_id = 'TEST'")).scalar()
        claim_count = db.execute(text("SELECT COUNT(*) FROM crosswalk_template WHERE client_id = 'TEST' AND file_group_name = 'CLAIM'")).scalar()
        member_count = db.execute(text("SELECT COUNT(*) FROM crosswalk_template WHERE client_id = 'TEST' AND file_group_name = 'MEMBER'")).scalar()
        provider_count = db.execute(text("SELECT COUNT(*) FROM crosswalk_template WHERE client_id = 'TEST' AND file_group_name = 'PROVIDER'")).scalar()
        
        print(f"\n✅ Data de-identification complete!")
        print(f"🛡️  Client changed from UPHP → TEST")
        print(f"📊 Total records updated: {total_updated}")
        print(f"📋 File group breakdown:")
        print(f"   • CLAIM: {claim_count} records")
        print(f"   • MEMBER: {member_count} records") 
        print(f"   • PROVIDER: {provider_count} records")
        print(f"🔒 All real data profiles replaced with dummy data")
        print(f"🎯 System ready for demo with de-identified data")
        
    except Exception as e:
        print(f"❌ Error de-identifying data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    de_identify_data()