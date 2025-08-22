"""
SQLAlchemy models for the Interactive Crosswalk & ETL Helper.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class DataModelField(Base):
    __tablename__ = "data_model_fields"
    
    id = Column(Integer, primary_key=True)
    model_table = Column(String, nullable=False)
    model_column = Column(String, nullable=False)
    description = Column(Text)
    data_type = Column(String)
    required = Column(Boolean, default=False)
    unique_key = Column(Boolean, default=False)

class SourceProfile(Base):
    __tablename__ = "source_profiles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    client_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    has_physical_file = Column(Boolean, default=False)
    raw_table_name = Column(String)
    
    # Relationships
    source_columns = relationship("SourceColumn", back_populates="profile", cascade="all, delete-orphan")
    crosswalk_mappings = relationship("CrosswalkMapping", back_populates="profile", cascade="all, delete-orphan")
    warehouse_configs = relationship("WarehouseConfig", back_populates="profile", cascade="all, delete-orphan")

class SourceColumn(Base):
    __tablename__ = "source_columns"
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("source_profiles.id"), nullable=False)
    source_column = Column(String, nullable=False)
    sample_values_json = Column(Text)  # JSON array of strings
    inferred_type = Column(String)  # string/number/date/boolean
    
    # Relationships
    profile = relationship("SourceProfile", back_populates="source_columns")
    regex_rules = relationship("RegexRule", back_populates="source_column", cascade="all, delete-orphan")
    crosswalk_mappings = relationship("CrosswalkMapping", back_populates="source_column", cascade="all, delete-orphan")

class CrosswalkMapping(Base):
    __tablename__ = "crosswalk_mappings"
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("source_profiles.id"), nullable=False)
    source_column_id = Column(Integer, ForeignKey("source_columns.id"), nullable=False)
    model_table = Column(String, nullable=False)
    model_column = Column(String, nullable=False)
    is_custom_field = Column(Boolean, default=False)
    custom_field_name = Column(String)
    transform_expression = Column(Text)
    notes = Column(Text)
    
    # Relationships
    profile = relationship("SourceProfile", back_populates="crosswalk_mappings")
    source_column = relationship("SourceColumn", back_populates="crosswalk_mappings")

class RegexRule(Base):
    __tablename__ = "regex_rules"
    
    id = Column(Integer, primary_key=True)
    source_column_id = Column(Integer, ForeignKey("source_columns.id"), nullable=False)
    rule_name = Column(String)
    pattern = Column(Text)
    flags = Column(String)  # e.g., 'i,m'
    description = Column(Text)
    
    # Relationships
    source_column = relationship("SourceColumn", back_populates="regex_rules")

class WarehouseConfig(Base):
    __tablename__ = "warehouse_configs"
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("source_profiles.id"), nullable=False)
    engine = Column(String)  # 'snowflake'
    account = Column(String)
    user = Column(String)
    role = Column(String)
    warehouse = Column(String)
    database = Column(String)
    schema = Column(String)
    private_key_path = Column(String)
    password_secret = Column(String)
    stored_procedure_call = Column(Text)  # Template with {RAW_TABLE}
    enabled = Column(Boolean, default=False)
    
    # Relationships
    profile = relationship("SourceProfile", back_populates="warehouse_configs")
