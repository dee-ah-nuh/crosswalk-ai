# Interactive Crosswalk & ETL Helper

A production-grade data engineering tool for mapping source data columns to standardized data models, with validation, transformation, and ETL configuration capabilities.

## Overview

This application helps data engineers and analysts:
- Map source columns from CSV/Excel files to predefined data model fields
- Create custom fields when needed
- Define and test regex validation rules
- Apply data transformation expressions using a built-in DSL
- Export mappings in multiple formats (CSV, Excel, JSON, SQL)
- Optionally fetch sample data from data warehouses

## Features

### Core Functionality
- **Two Input Modes**: Upload files (CSV/Excel) or define schema-only column lists
- **Interactive Grid**: Spreadsheet-like interface for column mapping
- **Data Model Integration**: Pre-defined target schema with required field validation
- **Custom Fields**: Support for fields not in the standard data model
- **Transform DSL**: Safe expression language for data transformations
- **Regex Validation**: Create and test regex patterns against sample data
- **Project Management**: Persistent storage with SQLite database

### Export Capabilities
- **CSV/Excel**: Traditional crosswalk format
- **JSON**: Pipeline configuration for ETL systems  
- **SQL**: Idempotent DDL/DML scripts with transformation views
- **Validation Reports**: Mapping completeness and rule compliance

### Optional Features
- **Warehouse Integration**: Fetch sample data via stored procedures (Snowflake)
- **Real-time Validation**: Live feedback on mapping progress and rule compliance
- **Bulk Operations**: Quick-fill and keyboard navigation for efficiency

## Technology Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- TanStack Table (data grid)
- Font Awesome (icons)

### Backend
- Python FastAPI
- SQLAlchemy (ORM)
- SQLite (database)
- pandas + openpyxl (file processing)
- Optional: snowflake-connector-python

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation & Startup

1. **Clone or set up the project structure**

2. **Install Python dependencies** (handled by Replit or pip):
```bash
pip install fastapi uvicorn sqlalchemy pandas openpyxl python-multipart
