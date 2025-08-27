# Interactive Crosswalk & ETL Helper

## Overview

A production-grade data engineering tool designed to streamline the process of mapping source data columns to standardized data models. The application enables data engineers to upload CSV/Excel files or define schema-only column lists, create interactive mappings to predefined data model fields, validate data using regex rules, and export configurations in multiple formats (CSV, Excel, JSON, SQL). The system supports custom field creation, data transformation using a built-in DSL, and optional data warehouse integration for fetching sample data.

## Recent Changes

**Deployment Fixes Applied (August 27, 2025)**
- Fixed crosswalk script executable permissions using `chmod +x crosswalk`
- Added proper shebang (#!/bin/bash) to crosswalk script
- Enhanced deploy.py with better error handling and fallback database seeding
- Created alternative deployment scripts (start.py) for maximum reliability
- Fixed import issues in deploy.py with try-catch error handling
- Verified all deployment commands work correctly (./crosswalk run, python deploy.py, python start.py)

## User Preferences

Preferred communication style: Simple, everyday language.
Run command: "crosswalk run" (uses unified deployment on port 5000)

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript for type safety and modern development practices
- **Build Tool**: Vite for fast development and optimized production builds
- **Styling**: Tailwind CSS for utility-first styling with custom design system
- **Data Grid**: TanStack Table for spreadsheet-like interface with editable cells and advanced features
- **State Management**: React hooks with custom data fetching hooks (`useProfiles`, `useCrosswalk`)
- **Component Structure**: Modular components including ProjectSidebar, CrosswalkGrid, DetailPanel, RegexTester, FileUpload, and SchemaInput

### Backend Architecture
- **Framework**: FastAPI for high-performance API development with automatic OpenAPI documentation
- **Database ORM**: SQLAlchemy with declarative models for type-safe database operations
- **Routing**: Modular route organization with separate modules for profiles, crosswalk mappings, and exports
- **File Processing**: pandas and openpyxl for robust CSV/Excel parsing and data inference
- **Data Transformation**: Custom DSL engine for safe expression evaluation and validation

### Data Storage Solutions
- **Primary Database**: SQLite for local persistence and simplicity
- **Schema Design**: Normalized relational schema with core entities:
  - `data_model_fields`: Predefined target schema fields
  - `source_profiles`: Project containers with metadata
  - `source_columns`: Source data column definitions with sample values
  - `crosswalk_mappings`: Column mapping configurations
  - `regex_rules`: Validation rule definitions
  - `warehouse_configs`: Optional data warehouse connection settings

### Authentication and Authorization
- **Current State**: No authentication implemented (internal tool assumption)
- **CORS Configuration**: Configured for local development with specific origin allowlist
- **Security Considerations**: Designed for internal network deployment with potential for future authentication integration

### Data Processing Pipeline
- **File Ingestion**: Multi-format support (CSV, XLSX, XLS) with automatic type inference
- **Schema Processing**: Support for schema-only workflows without physical files
- **Validation Engine**: Real-time regex validation with testing capabilities
- **Transform Engine**: Safe DSL for data transformations with function validation
- **Export Pipeline**: Multi-format output generation (CSV, Excel, JSON, SQL DDL/DML)

## External Dependencies

### Core Dependencies
- **React Ecosystem**: React 18, TypeScript, Vite for modern frontend development
- **Python Backend**: FastAPI, SQLAlchemy, pandas, openpyxl for robust data processing
- **Styling and UI**: Tailwind CSS, Font Awesome icons, TanStack Table for professional interface

### Optional Integrations
- **Data Warehouse**: Snowflake connector for sample data fetching (feature-flagged)
- **Database Flexibility**: Architecture supports migration from SQLite to PostgreSQL or other databases
- **Export Formats**: Built-in support for CSV, Excel, JSON, and SQL export without external services

### Development Tools
- **Build and Bundling**: Vite with optimized chunk splitting and vendor separation
- **Type Safety**: TypeScript configuration with strict mode and path mapping
- **Code Organization**: Modular architecture with clear separation of concerns

### Environment Configuration
- **Development Server**: Built-in proxy configuration for API routing
- **Production Deployment**: Static file serving with FastAPI backend using unified port 5000
- **Feature Toggles**: Environment-based configuration for optional features like warehouse connectivity
- **Run Commands**: Multiple deployment options for reliability
  - `./crosswalk run` or `crosswalk run`: Start production server with unified frontend/backend (primary)
  - `./crosswalk dev` or `crosswalk dev`: Start development mode with separate ports
  - `./crosswalk build` or `crosswalk build`: Build frontend only
  - `./crosswalk help` or `crosswalk help`: Show available commands
  - `python deploy.py`: Direct deployment script execution (alternative)
  - `python start.py`: Alternative deployment script (fallback)