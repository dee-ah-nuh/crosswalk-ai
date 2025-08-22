#!/usr/bin/env python3
"""
Standalone database seeding script for the Interactive Crosswalk & ETL Helper.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from models import Base, DataModelField

def seed_database():
    """Seed the database with initial data"""
    # Get database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is required")
        sys.exit(1)
    
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Seed data
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_fields = db.query(DataModelField).first()
        if existing_fields:
            print("✅ Seed data already exists, skipping...")
            return
        
        # Define seed data
        seed_fields = [
            # CLAIM table
            {
                "model_table": "CLAIM",
                "model_column": "CLAIM_ID",
                "description": "Unique identifier for the claim",
                "data_type": "VARCHAR(50)",
                "required": True,
                "unique_key": True
            },
            {
                "model_table": "CLAIM",
                "model_column": "MEMBER_ID",
                "description": "Member/Patient identifier",
                "data_type": "VARCHAR(50)",
                "required": True,
                "unique_key": False
            },
            {
                "model_table": "CLAIM",
                "model_column": "CLAIM_TYPE",
                "description": "Type of claim (MEDICAL, PHARM, etc.)",
                "data_type": "VARCHAR(20)",
                "required": True,
                "unique_key": False
            },
            {
                "model_table": "CLAIM",
                "model_column": "SERVICE_DATE",
                "description": "Date of service",
                "data_type": "DATE",
                "required": True,
                "unique_key": False
            },
            {
                "model_table": "CLAIM",
                "model_column": "AMOUNT",
                "description": "Claim amount",
                "data_type": "DECIMAL(10,2)",
                "required": False,
                "unique_key": False
            },
            {
                "model_table": "CLAIM",
                "model_column": "PLAN_CODE",
                "description": "Insurance plan code",
                "data_type": "VARCHAR(20)",
                "required": False,
                "unique_key": False
            },
            
            # PROVIDER table
            {
                "model_table": "PROVIDER",
                "model_column": "NPI",
                "description": "National Provider Identifier",
                "data_type": "VARCHAR(10)",
                "required": True,
                "unique_key": True
            },
            {
                "model_table": "PROVIDER",
                "model_column": "PROVIDER_NAME",
                "description": "Provider name",
                "data_type": "VARCHAR(255)",
                "required": True,
                "unique_key": False
            },
            {
                "model_table": "PROVIDER",
                "model_column": "TAXONOMY",
                "description": "Provider taxonomy code",
                "data_type": "VARCHAR(50)",
                "required": False,
                "unique_key": False
            },
            {
                "model_table": "PROVIDER",
                "model_column": "SPECIALTY",
                "description": "Provider specialty",
                "data_type": "VARCHAR(100)",
                "required": False,
                "unique_key": False
            },
            {
                "model_table": "PROVIDER",
                "model_column": "ADDRESS_STATE",
                "description": "Provider state",
                "data_type": "VARCHAR(2)",
                "required": False,
                "unique_key": False
            },
            
            # PLAN table
            {
                "model_table": "PLAN",
                "model_column": "PLAN_CODE",
                "description": "Plan identifier code",
                "data_type": "VARCHAR(20)",
                "required": True,
                "unique_key": True
            },
            {
                "model_table": "PLAN",
                "model_column": "PLAN_NAME",
                "description": "Plan name",
                "data_type": "VARCHAR(255)",
                "required": True,
                "unique_key": False
            },
            {
                "model_table": "PLAN",
                "model_column": "PLAN_TYPE",
                "description": "Type of plan (HMO, PPO, etc.)",
                "data_type": "VARCHAR(20)",
                "required": False,
                "unique_key": False
            },
            {
                "model_table": "PLAN",
                "model_column": "EFFECTIVE_DATE",
                "description": "Plan effective date",
                "data_type": "DATE",
                "required": False,
                "unique_key": False
            }
        ]
        
        # Insert seed data
        for field_data in seed_fields:
            field = DataModelField(**field_data)
            db.add(field)
        
        db.commit()
        print("✅ Seed data inserted successfully")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()