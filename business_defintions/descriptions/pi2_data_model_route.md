# PI20 Data Model Grid - Complete Setup Guide

This document outlines all the files, configurations, and components required for proper data flow between the frontend and backend for the PI20 Data Model Grid functionality.

## Overview
The PI20 Data Model Grid displays healthcare data model fields from a DuckDB database to the React frontend. Data flows from the `pi20_data_model` table through a FastAPI backend to a React component.

## Backend Components

### 1. Database Setup

#### Required Files:
- **`backend/database/ddl/tables/create_pi20_data_model.py`** - Creates and populates the `pi20_data_model` table
- **`business_defintions/pi20_data_model.csv`** - Source data file containing the PI20 data model fields

#### Database Table Structure:
```sql
CREATE TABLE IF NOT EXISTS pi20_data_model (
  IN_CROSSWALK VARCHAR,
  TABLE_NAME VARCHAR,
  COLUMN_NAME VARCHAR,
  COLUMN_TYPE VARCHAR,
  COLUMN_ORDER INTEGER,
  COLUMN_COMMENT VARCHAR,
  TABLE_CREATION_ORDER INTEGER,
  IS_MANDATORY BOOLEAN,
  MANDATORY_PROV_TYPE VARCHAR,
  MCDM_MASKING_TYPE VARCHAR,
  IN_EDITS BOOLEAN,
  KEY VARCHAR
);
```

### 2. Backend API Route

#### Required Files:
- **`backend/database/routes/datamodel.py`** - Main API route file

#### Key Components:

**Pydantic Response Model:**
```python
class DataModelField(BaseModel):
    id: int
    schema_layer: str  # IN_CROSSWALK
    table_name: str
    column_name: str
    data_type: str  # COLUMN_TYPE
    column_order: int
    description: str  # COLUMN_COMMENT
    table_creation_order: int
    is_mandatory: bool  # IS_MANDATORY
    mandatory_prov_type: str  # MANDATORY_PROV_TYPE
    mcdm_masking_type: str  # MCDM_MASKING_TYPE
    in_edits: bool  # IN_EDITS
    key: str  # KEY
    is_standard_field: bool = True  # Computed field
    is_case_sensitive: bool = True  # Computed field
```

**API Endpoint:**
```python
@router.get("", response_model=List[DataModelField])
async def get_data_model_fields(...)
```

**SQL Query:**
```sql
SELECT 
    ROW_NUMBER() OVER (ORDER BY TABLE_NAME, COLUMN_NAME) as id,
    IN_CROSSWALK,
    TABLE_NAME,
    COLUMN_NAME,
    COLUMN_TYPE,
    COLUMN_ORDER,
    COLUMN_COMMENT,
    TABLE_CREATION_ORDER,
    IS_MANDATORY,
    MANDATORY_PROV_TYPE,
    MCDM_MASKING_TYPE,
    IN_EDITS,
    KEY
FROM pi20_data_model
WHERE 1=1
ORDER BY table_name, column_name
```

### 3. Database Connection

#### Required Files:
- **`backend/database/duckdb_cxn.py`** - Database connection manager
- **`backend/database/models.py`** - SQLAlchemy models (if used)

### 4. FastAPI Application Setup

#### Required Files:
- **`backend/app.py`** - Main FastAPI application
- **`backend/database/routes/__init__.py`** - Router initialization

#### Required Imports in app.py:
```python
from database.routes import datamodel
app.include_router(datamodel.router)
```

## Frontend Components

### 1. API Service Layer

#### Required Files:
- **`frontend/src/services/api.ts`** - API client with proper URL handling

#### Critical Fix for URL Construction:
```typescript
async get(endpoint: string, params?: Record<string, string>) {
  let url: string;
  const fullPath = `${API_BASE_URL}${endpoint}`;
  
  if (params) {
    const urlObj = new URL(fullPath, window.location.origin);
    Object.entries(params).forEach(([key, value]) => {
      urlObj.searchParams.append(key, value);
    });
    url = urlObj.toString();
  } else {
    url = fullPath;
  }

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  return this.handleResponse(response);
}
```

### 2. TypeScript Interface

#### Required Files:
- **`frontend/src/components/PI20DataModelGrid.tsx`** - Main component file

#### TypeScript Interface (must match backend Pydantic model):
```typescript
interface PI20DataModelField {
  id: number;
  schema_layer: string;
  table_name: string;
  column_name: string;
  data_type: string;
  column_order: number;
  description: string;
  table_creation_order: number;
  is_mandatory: boolean;
  mandatory_prov_type: string;
  mcdm_masking_type: string;
  in_edits: boolean;
  key: string;
  is_standard_field: boolean;
  is_case_sensitive: boolean;
}
```

### 3. React Component

#### Required Files:
- **`frontend/src/components/PI20DataModelGrid.tsx`** - Main React component

#### Key Component Functions:
```typescript
const fetchPI20Data = async () => {
  try {
    setLoading(true);
    const response = await api.get('/datamodel');
    setData(response);
  } catch (error) {
    console.error('Error fetching PI20 data model:', error);
  } finally {
    setLoading(false);
  }
};
```

## Configuration Files

### 1. Vite Configuration (Frontend Proxy)

#### Required Files:
- **`frontend/vite.config.ts`** - Development server configuration

#### Required Proxy Configuration:
```typescript
export default defineConfig({
  // ... other config
  server: {
    proxy: {
      '/api': {
        target: 'http://0.0.0.0:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
```

### 2. API Base URL Configuration

#### Required Configuration in api.ts:
```typescript
const API_BASE_URL = '/api';
```

## Startup Scripts

### Required Files:
- **`start.sh`** - Starts both backend and frontend
- **`shutdown.sh`** - Stops both services

## Data Flow Verification Checklist

### Backend Verification:
1. **Database populated**: `SELECT COUNT(*) FROM pi20_data_model;` should return > 0
2. **API endpoint accessible**: `curl http://localhost:8000/api/datamodel` should return JSON array
3. **All fields present**: Response should include all 15 fields (id + 12 database columns + 2 computed fields)
4. **Proper data types**: Check that integers are returned as numbers, booleans as booleans

### Frontend Verification:
1. **Proxy working**: `curl http://localhost:1234/api/datamodel` should return same data as backend
2. **TypeScript interface matches**: No compilation errors
3. **Component renders**: Loading state → Data display → Table populated
4. **All columns visible**: Table should show Table, Column, Data Type, etc.

## Common Issues and Solutions

### 1. "Invalid URL" Error
**Cause**: Using `new URL()` with relative paths
**Solution**: Use the fixed `get()` method in api.ts (see above)

### 2. Empty Data Grid
**Cause**: Interface mismatch between frontend and backend
**Solution**: Ensure TypeScript interface exactly matches Pydantic model

### 3. Missing ID Field
**Cause**: Backend not returning `id` field
**Solution**: Add `ROW_NUMBER()` to SQL query and include in response mapping

### 4. Proxy Not Working
**Cause**: Vite proxy misconfiguration
**Solution**: Verify proxy configuration in vite.config.ts

### 5. CORS Issues
**Cause**: Backend not allowing frontend origin
**Solution**: Verify CORS middleware in app.py allows frontend origin

## Testing Commands

```bash
# Test backend API directly
curl -X GET "http://localhost:8000/api/datamodel" | jq '.[0]'

# Test frontend proxy
curl -X GET "http://localhost:1234/api/datamodel" | jq '.[0]'

# Check database content
# Connect to DuckDB and run: SELECT COUNT(*) FROM pi20_data_model;
```

This comprehensive setup ensures proper data flow from the database through the backend API to the frontend React component.
