"""
DuckDB-compatible SQLAlchemy models for the Crosswalk Aarete.
This file contains only ORM table/class definitions optimized for DuckDB.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Identity
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class DataModelField(Base):
    __tablename__ = "x"
    id = Column(Integer, Identity(always=True), primary_key=True)
    model_table = Column(String, nullable=False)
    model_column = Column(String, nullable=False)
    description = Column(Text)
    data_type = Column(String)
    required = Column(Boolean, default=False)
    unique_key = Column(Boolean, default=False)

class SourceProfile(Base):
    __tablename__ = "source_profiles"
    id = Column(Integer, primary_key=True)  # DuckDB auto-increment
    name = Column(String, nullable=False)
    client_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    has_physical_file = Column(Boolean, default=False)
    raw_table_name = Column(String)
    source_columns = relationship("SourceColumn", back_populates="profile", cascade="all, delete-orphan")
    crosswalk_mappings = relationship("CrosswalkMapping", back_populates="profile", cascade="all, delete-orphan")
    warehouse_configs = relationship("WarehouseConfig", back_populates="profile", cascade="all, delete-orphan")

class SourceColumn(Base):
    __tablename__ = "source_columns"
    id = Column(Integer, primary_key=True)  # DuckDB auto-increment
    profile_id = Column(Integer, ForeignKey("source_profiles.id"), nullable=False)
    source_column = Column(String, nullable=False)
    sample_values_json = Column(Text)
    inferred_type = Column(String)
    profile = relationship("SourceProfile", back_populates="source_columns")
    regex_rules = relationship("RegexRule", back_populates="source_column", cascade="all, delete-orphan")
    crosswalk_mappings = relationship("CrosswalkMapping", back_populates="source_column", cascade="all, delete-orphan")

class CrosswalkMapping(Base):
    __tablename__ = "crosswalk_mappings"
    id = Column(Integer, primary_key=True)  # DuckDB auto-increment
    profile_id = Column(Integer, ForeignKey("source_profiles.id"), nullable=False)
    source_column_id = Column(Integer, ForeignKey("source_columns.id"), nullable=False)
    model_table = Column(String, nullable=False)
    model_column = Column(String, nullable=False)
    is_custom_field = Column(Boolean, default=False)
    custom_field_name = Column(String)
    transform_expression = Column(Text)
    notes = Column(Text)
    profile = relationship("SourceProfile", back_populates="crosswalk_mappings")
    source_column = relationship("SourceColumn", back_populates="crosswalk_mappings")

class RegexRule(Base):
    __tablename__ = "regex_rules"
    id = Column(Integer, primary_key=True)  # DuckDB auto-increment
    source_column_id = Column(Integer, ForeignKey("source_columns.id"), nullable=False)
    rule_name = Column(String)
    pattern = Column(Text)
    flags = Column(String)
    description = Column(Text)
    source_column = relationship("SourceColumn", back_populates="regex_rules")

class WarehouseConfig(Base):
    __tablename__ = "warehouse_configs"
    id = Column(Integer, primary_key=True)  # DuckDB auto-increment
    profile_id = Column(Integer, ForeignKey("source_profiles.id"), nullable=False)
    engine = Column(String)
    account = Column(String)
    user = Column(String)
    role = Column(String)
    warehouse = Column(String)
    database = Column(String)
    schema = Column(String)
    private_key_path = Column(String)
    password_secret = Column(String)
    stored_procedure_call = Column(Text)
    enabled = Column(Boolean, default=False)
    profile = relationship("SourceProfile", back_populates="warehouse_configs")
