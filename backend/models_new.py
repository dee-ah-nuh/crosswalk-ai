"""
Updated models to match the crosswalk template structure
"""

from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class CrosswalkTemplate(Base):
    """Main crosswalk mapping table - matches your Excel template structure"""
    __tablename__ = "crosswalk_template"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core identification fields (columns 1-5 from Excel)
    client_id = Column(String(100), nullable=False, index=True)
    source_column_order = Column(Integer)
    source_column_name = Column(String(255), nullable=False, index=True)
    file_group_name = Column(String(100), nullable=False, index=True)  # CLAIM, CLAIM_LINE, MEMBER, PROVIDER
    mcdm_column_name = Column(String(255))
    
    # Data flow control (columns 6-8)
    in_model = Column(String(10), default='Y')  # Y, N, U, N/A
    mcdm_table = Column(String(100))
    custom_field_type = Column(String(50))
    
    # Data profiling fields (columns 9-14 from Excel - calculated from Profile sheet)
    data_profile_info = Column(Text)  # Main profile info
    profile_column_2 = Column(Text)
    profile_column_3 = Column(Text)
    profile_column_4 = Column(Text)
    profile_column_5 = Column(Text)
    profile_column_6 = Column(Text)
    
    # Transformation and control (columns 15-16)
    source_column_formatting = Column(Text)  # Formula for data transformation
    skipped_flag = Column(Boolean, default=False)  # TRUE to skip field
    
    # Additional fields for remaining columns
    additional_field_1 = Column(Text)
    additional_field_2 = Column(Text)
    additional_field_3 = Column(Text)
    additional_field_4 = Column(Text)
    additional_field_5 = Column(Text)
    additional_field_6 = Column(Text)
    additional_field_7 = Column(Text)
    additional_field_8 = Column(Text)
    
    # Tracking
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ClientProfile(Base):
    """Client profile configurations"""
    __tablename__ = "client_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(100), nullable=False)
    client_name = Column(String(255), nullable=False)
    file_group_name = Column(String(100), nullable=False)
    version = Column(String(50), default='V00')
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('client_id', 'file_group_name', 'version'),)

class DataModelReference(Base):
    """Reference data model (from your Data Model sheet)"""
    __tablename__ = "data_model_reference"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False)
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(100))
    description = Column(Text)
    is_required = Column(Boolean, default=False)
    is_unique_key = Column(Boolean, default=False)
    default_value = Column(Text)
    validation_rules = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (UniqueConstraint('table_name', 'column_name'),)

class ProfileData(Base):
    """Profile data for formula lookups (matches your Profile sheet)"""
    __tablename__ = "profile_data"
    
    id = Column(Integer, primary_key=True, index=True)
    lookup_key = Column(String(500), nullable=False, unique=True, index=True)  # CLIENT_ID-FILE_GROUP_NAME-VERSION-COLUMN_NAME
    client_id = Column(String(100), nullable=False)
    file_group_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    column_name = Column(String(255), nullable=False)
    data_profile = Column(Text)
    profile_value_1 = Column(Text)
    profile_value_2 = Column(Text)
    profile_value_3 = Column(Text)
    profile_value_4 = Column(Text)
    profile_value_5 = Column(Text)
    sample_values = Column(Text)  # JSON array of sample values
    created_at = Column(DateTime, default=func.now())