# Component Flow Documentation

This document traces the complete data flow for each component in the `/frontend/src/components/` directory, showing how they connect to the backend APIs and database.

---

## **1. CrosswalkDetailPanel.tsx**

### **Purpose**: Side panel for editing individual crosswalk mappings

### **Flow**: CrosswalkDetailPanel → Backend → Database

#### **1. User Interaction**
```tsx
// User fills form and clicks "Save Changes"
const handleSave = () => {
  onUpdateMapping(formData);  // ← Flow starts here
  onClose();
};

// formData contains:
{
  source_column_name: "FIRST_NAME",
  mcdm_column_name: "patient_first_name", 
  in_model: "Y",
  custom_data_type: "VARCHAR(50)",
  // ... other fields
}
```

#### **2. Parent Component Receives Update**
```tsx
// Parent component (CrosswalkGrid.tsx) receives the callback:
const handleUpdateMapping = async (updates: Partial<CrosswalkMapping>) => {
  const result = await crosswalkApi.updateMapping(selectedMapping.id, updates);
};
```

#### **3. Frontend API Service (crosswalkApi.ts)**
```typescript
async updateMapping(id: number, data: Partial<CrosswalkMapping>) {
  const response = await fetch(`/api/crosswalk/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
}
```

#### **4. Backend Route Handler**
```python
# backend/database/routes/crosswalk.py
@router.put("/crosswalk/{mapping_id}")
async def update_crosswalk_mapping(mapping_id: int, mapping_data: dict):
    # UPDATE crosswalk_template SET ... WHERE id = mapping_id
```

#### **5. Database Update**
```sql
-- DuckDB: crosswalk.duckdb
UPDATE crosswalk_template 
SET source_column_name = 'FIRST_NAME',
    mcdm_column_name = 'patient_first_name',
    updated_at = CURRENT_TIMESTAMP
WHERE id = 123;
```

**API Endpoints Used**: `PUT /api/crosswalk/{id}`

---

## **2. CrosswalkGrid.tsx**

### **Purpose**: Main data grid displaying crosswalk mappings with filtering and editing

### **Flow**: CrosswalkGrid → Backend → Database

#### **1. Component Mount & Data Loading**
```tsx
useEffect(() => {
  const loadData = async () => {
    const mappings = await crosswalkApi.getCrosswalkMappings({
      client_id: selectedClient,
      file_group: selectedFileGroup,
      limit: 500
    });
    setMappings(mappings);
  };
  loadData();
}, [selectedClient, selectedFileGroup]);
```

#### **2. Frontend API Service**
```typescript
async getCrosswalkMappings(params?: {
  client_id?: string;
  file_group?: string;
  limit?: number;
  offset?: number;
}): Promise<CrosswalkMapping[]> {
  const urlParams = new URLSearchParams();
  if (params?.client_id) urlParams.append('client_id', params.client_id);
  
  const response = await fetch(`/api/crosswalk?${urlParams}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  
  const data = await response.json();
  return data.data || data;
}
```

#### **3. Backend Route Handler**
```python
# backend/database/routes/crosswalk.py
@router.get("/crosswalk")
async def get_crosswalk_data(
    client_id: str = None,
    file_group: str = None,
    limit: int = 500,
    offset: int = 0
):
    # SELECT * FROM crosswalk_template WHERE ... LIMIT ... OFFSET ...
```

#### **4. Database Query**
```sql
-- DuckDB: crosswalk.duckdb
SELECT id, client_id, source_column_name, mcdm_column_name, 
       in_model, mcdm_table, created_at, updated_at
FROM crosswalk_template 
WHERE client_id = 'TEST' AND file_group_name = 'CLAIM'
ORDER BY source_column_order, source_column_name
LIMIT 500 OFFSET 0;
```

#### **5. User Interactions**
- **Edit Row**: Opens `CrosswalkDetailPanel`
- **Filter by Client**: Calls `getCrosswalkMappings()` with new client_id
- **Filter by File Group**: Calls `getCrosswalkMappings()` with new file_group

**API Endpoints Used**: 
- `GET /api/crosswalk` (with query parameters)
- `GET /api/crosswalk/clients`
- `GET /api/crosswalk/file-groups`

---

## **3. FileUpload.tsx**

### **Purpose**: Upload CSV/Excel files to populate crosswalk mappings

### **Flow**: FileUpload → Backend → Database

#### **1. File Selection & Upload**
```tsx
const handleFileUpload = async (file: File, clientId: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('client_id', clientId);
  
  // Call upload API ↓
  const result = await crosswalkApi.uploadSourceColumns(formData);
};
```

#### **2. Frontend API Service**
```typescript
async uploadSourceColumns(formData: FormData): Promise<{success: boolean; message: string}> {
  const response = await fetch('/api/profiles/upload', {
    method: 'POST',
    body: formData, // No Content-Type header for FormData
  });
  return response.json();
}
```

#### **3. Backend Route Handler**
```python
# backend/database/routes/profiles.py
@router.post("/profiles/upload")
async def upload_source_columns(file: UploadFile, client_id: str):
    # Parse CSV/Excel file
    # Extract column names and metadata
    # Insert into source_columns table
    # Return success/error response
```

#### **4. Database Insert**
```sql
-- DuckDB: crosswalk.duckdb
INSERT INTO source_columns (
    client_id, source_column_name, source_column_order, 
    file_group_name, created_at
) VALUES 
    ('TEST', 'FIRST_NAME', 1, 'CLAIM', CURRENT_TIMESTAMP),
    ('TEST', 'LAST_NAME', 2, 'CLAIM', CURRENT_TIMESTAMP),
    ('TEST', 'CLAIM_NUMBER', 3, 'CLAIM', CURRENT_TIMESTAMP);
```

**API Endpoints Used**: `POST /api/profiles/upload`

---

## **4. SnowflakeExportModal.tsx**

### **Purpose**: Generate Snowflake DDL/DML SQL from crosswalk mappings

### **Flow**: SnowflakeExportModal → Backend → SQL Generation

#### **1. User Configures Export**
```tsx
const handleGenerateSQL = async () => {
  const exportData = {
    client_id: selectedClient,
    file_group: selectedFileGroup,
    export_type: 'CREATE_TABLE', // or 'INSERT_STATEMENTS'
    table_name: tableName,
    created_by: userName
  };
  
  const result = await crosswalkApi.generateSnowflakeSQL(exportData);
  setSqlContent(result.sql_content);
};
```

#### **2. Frontend API Service**
```typescript
async generateSnowflakeSQL(exportData: {
  client_id: string;
  file_group?: string;
  export_type: string;
  table_name: string;
  created_by?: string;
}): Promise<{sql_content: string; table_name: string; export_type: string; mapping_count: number}> {
  const response = await fetch('/api/snowflake/generate-sql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(exportData),
  });
  return response.json();
}
```

#### **3. Backend Route Handler**
```python
# backend/database/routes/snowflake_export.py
@router.post("/snowflake/generate-sql")
async def generate_snowflake_sql(export_data: dict):
    # Query crosswalk mappings
    # Generate CREATE TABLE statement
    # Generate INSERT statements or COPY commands
    # Return generated SQL
```

#### **4. Database Query & SQL Generation**
```sql
-- Query: Get mappings for SQL generation
SELECT source_column_name, mcdm_column_name, custom_data_type, in_model
FROM crosswalk_template 
WHERE client_id = 'TEST' AND file_group_name = 'CLAIM';

-- Generated Output:
CREATE TABLE patient_claims (
    patient_first_name VARCHAR(50),
    patient_last_name VARCHAR(50),
    claim_number VARCHAR(20),
    service_date DATE
);
```

**API Endpoints Used**: 
- `POST /api/snowflake/generate-sql`
- `GET /api/snowflake/exports`

---

## **5. Navigation.tsx**

### **Purpose**: Top navigation bar with route switching and summary stats

### **Flow**: Navigation → Backend → Dashboard Data

#### **1. Component Mount & Stats Loading**
```tsx
useEffect(() => {
  const loadSummary = async () => {
    const summary = await crosswalkApi.getSummary();
    setSummaryData(summary);
  };
  loadSummary();
}, []);
```

#### **2. Frontend API Service**
```typescript
async getSummary(): Promise<CrosswalkSummary> {
  const response = await fetch('/api/crosswalk/summary', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
}
```

#### **3. Backend Route Handler**
```python
# backend/database/routes/crosswalk.py
@router.get("/crosswalk/summary")
async def get_summary():
    # Aggregate queries for dashboard stats
    return {
        "total_mappings": total_count,
        "total_clients": client_count,
        "total_file_groups": file_group_count,
        "skipped_fields": skipped_count
    }
```

#### **4. Database Aggregation Queries**
```sql
-- Multiple queries for summary stats
SELECT COUNT(*) as total_mappings FROM crosswalk_template;
SELECT COUNT(DISTINCT client_id) as total_clients FROM crosswalk_template;
SELECT COUNT(*) as skipped_fields FROM crosswalk_template WHERE skipped_flag = true;
```

**API Endpoints Used**: `GET /api/crosswalk/summary`

---

## **6. PI20DataModelGrid.tsx**

### **Purpose**: Display and manage the PI20 data model structure

### **Flow**: PI20DataModelGrid → Backend → PI20 Model Data

#### **1. Data Loading**
```tsx
useEffect(() => {
  const loadDataModel = async () => {
    const modelData = await dataModelApi.getPI20DataModel();
    setModelData(modelData);
  };
  loadDataModel();
}, []);
```

#### **2. Frontend API Service**
```typescript
// In dataModelApi.ts
async getPI20DataModel(): Promise<PI20DataModel[]> {
  const response = await fetch('/api/datamodel/pi20', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
}
```

#### **3. Backend Route Handler**
```python
# backend/database/routes/datamodel.py
@router.get("/datamodel/pi20")
async def get_pi20_data_model():
    # SELECT * FROM pi20_data_model ORDER BY table_name, column_order
```

#### **4. Database Query**
```sql
-- DuckDB: crosswalk.duckdb
SELECT table_name, column_name, data_type, is_required, 
       description, column_order
FROM pi20_data_model 
ORDER BY table_name, column_order;
```

**API Endpoints Used**: `GET /api/datamodel/pi20`

---

## **7. MCSReviewScreen.tsx**

### **Purpose**: Medical Coding Specialist review workflow for mappings

### **Flow**: MCSReviewScreen → Backend → Review Updates

#### **1. Load Pending Reviews**
```tsx
useEffect(() => {
  const loadPendingReviews = async () => {
    const reviews = await crosswalkApi.getPendingReviews();
    setPendingReviews(reviews);
  };
  loadPendingReviews();
}, []);
```

#### **2. Submit Review**
```tsx
const handleSubmitReview = async (mappingId: number, reviewData: {
  status: 'APPROVED' | 'REJECTED' | 'NEEDS_CHANGES';
  notes: string;
  reviewer: string;
}) => {
  await crosswalkApi.submitMCSReview(mappingId, reviewData);
  // Refresh pending reviews
};
```

#### **3. Frontend API Service**
```typescript
async submitMCSReview(mappingId: number, reviewData: {
  status: string;
  notes: string;
  reviewer: string;
}): Promise<{success: boolean; message: string}> {
  const response = await fetch(`/api/crosswalk/${mappingId}/mcs-review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reviewData),
  });
  return response.json();
}
```

#### **4. Backend Route Handler**
```python
# backend/database/routes/crosswalk.py
@router.post("/crosswalk/{mapping_id}/mcs-review")
async def submit_mcs_review(mapping_id: int, review_data: dict):
    # UPDATE crosswalk_template SET mcs_review_status = ..., mcs_review_notes = ...
```

#### **5. Database Update**
```sql
-- DuckDB: crosswalk.duckdb
UPDATE crosswalk_template 
SET mcs_review_status = 'APPROVED',
    mcs_review_notes = 'Mapping looks correct',
    mcs_reviewer = 'john.doe@company.com',
    mcs_review_date = CURRENT_TIMESTAMP
WHERE id = 123;
```

**API Endpoints Used**: 
- `GET /api/crosswalk/pending-reviews`
- `POST /api/crosswalk/{id}/mcs-review`

---

## **8. RegexTester.tsx**

### **Purpose**: Test regex patterns for data validation and transformation

### **Flow**: RegexTester → Backend → Pattern Validation

#### **1. Test Regex Pattern**
```tsx
const handleTestRegex = async (pattern: string, testData: string[]) => {
  const result = await crosswalkApi.testRegexPattern({
    pattern,
    test_data: testData,
    flags: 'gi'
  });
  setTestResults(result);
};
```

#### **2. Frontend API Service**
```typescript
async testRegexPattern(data: {
  pattern: string;
  test_data: string[];
  flags?: string;
}): Promise<{matches: Array<{input: string; matches: string[]; is_match: boolean}>}> {
  const response = await fetch('/api/regex/test', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
}
```

#### **3. Backend Route Handler**
```python
# backend/database/routes/regex.py
@router.post("/regex/test")
async def test_regex_pattern(pattern_data: dict):
    import re
    pattern = pattern_data['pattern']
    test_data = pattern_data['test_data']
    
    results = []
    for text in test_data:
        matches = re.findall(pattern, text)
        results.append({
            'input': text,
            'matches': matches,
            'is_match': len(matches) > 0
        })
    
    return {'matches': results}
```

**API Endpoints Used**: `POST /api/regex/test`

---

## **9. CrosswalkTemplateGrid.tsx**

### **Purpose**: Manage crosswalk templates and reusable mappings

### **Flow**: CrosswalkTemplateGrid → Backend → Template Management

#### **1. Load Templates**
```tsx
useEffect(() => {
  const loadTemplates = async () => {
    const templates = await crosswalkApi.getCrosswalkTemplates();
    setTemplates(templates);
  };
  loadTemplates();
}, []);
```

#### **2. Create Template from Existing Mappings**
```tsx
const handleCreateTemplate = async (templateData: {
  name: string;
  description: string;
  source_mappings: number[];
}) => {
  const result = await crosswalkApi.createTemplate(templateData);
  if (result.success) {
    await loadTemplates(); // Refresh
  }
};
```

#### **3. Frontend API Service**
```typescript
async createTemplate(templateData: {
  name: string;
  description: string;
  source_mappings: number[];
}): Promise<{success: boolean; template_id: number; message: string}> {
  const response = await fetch('/api/crosswalk/templates', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(templateData),
  });
  return response.json();
}
```

#### **4. Backend Route Handler**
```python
# backend/database/routes/crosswalk.py
@router.post("/crosswalk/templates")
async def create_crosswalk_template(template_data: dict):
    # INSERT INTO crosswalk_templates (name, description, ...)
    # Copy mappings to template_mappings table
```

**API Endpoints Used**: 
- `GET /api/crosswalk/templates`
- `POST /api/crosswalk/templates`
- `PUT /api/crosswalk/templates/{id}`

---

## **10. ProjectSidebar.tsx**

### **Purpose**: Project navigation and quick stats

### **Flow**: ProjectSidebar → Backend → Project Data

#### **1. Load Project Stats**
```tsx
useEffect(() => {
  const loadProjectData = async () => {
    const [clients, summary] = await Promise.all([
      crosswalkApi.getClients(),
      crosswalkApi.getSummary()
    ]);
    setClients(clients);
    setSummary(summary);
  };
  loadProjectData();
}, []);
```

**API Endpoints Used**: 
- `GET /api/crosswalk/clients`
- `GET /api/crosswalk/summary`

---

## **11. UploadScreen.tsx**

### **Purpose**: Batch upload interface for multiple files

### **Flow**: UploadScreen → Backend → Batch Processing

#### **1. Multi-file Upload**
```tsx
const handleBatchUpload = async (files: File[], clientId: string) => {
  const results = await Promise.all(
    files.map(file => crosswalkApi.uploadSourceColumns(
      createFormData(file, clientId)
    ))
  );
  // Process results
};
```

**API Endpoints Used**: `POST /api/profiles/upload` (multiple calls)

---

## **12. SchemaInput.tsx**

### **Purpose**: Manual schema definition and column mapping

### **Flow**: SchemaInput → Backend → Schema Storage

#### **1. Save Schema Definition**
```tsx
const handleSaveSchema = async (schemaData: {
  client_id: string;
  file_group: string;
  columns: Array<{name: string; type: string; required: boolean}>;
}) => {
  const result = await crosswalkApi.saveSchemaDefinition(schemaData);
};
```

**API Endpoints Used**: `POST /api/schema/definition`

---

## **13. DetailPanel.tsx**

### **Purpose**: Generic detail panel for various data types

### **Flow**: Similar to CrosswalkDetailPanel but more generic

**API Endpoints Used**: Varies based on data type being edited

---

## **Summary of All API Endpoints Used**

| **Component** | **Primary Endpoints** |
|---------------|----------------------|
| CrosswalkDetailPanel | `PUT /api/crosswalk/{id}` |
| CrosswalkGrid | `GET /api/crosswalk`, `GET /api/crosswalk/clients`, `GET /api/crosswalk/file-groups` |
| FileUpload | `POST /api/profiles/upload` |
| SnowflakeExportModal | `POST /api/snowflake/generate-sql`, `GET /api/snowflake/exports` |
| Navigation | `GET /api/crosswalk/summary` |
| PI20DataModelGrid | `GET /api/datamodel/pi20` |
| MCSReviewScreen | `GET /api/crosswalk/pending-reviews`, `POST /api/crosswalk/{id}/mcs-review` |
| RegexTester | `POST /api/regex/test` |
| CrosswalkTemplateGrid | `GET /api/crosswalk/templates`, `POST /api/crosswalk/templates` |
| ProjectSidebar | `GET /api/crosswalk/clients`, `GET /api/crosswalk/summary` |
| UploadScreen | `POST /api/profiles/upload` |
| SchemaInput | `POST /api/schema/definition` |

This documentation shows how each component connects to your FastAPI backend and ultimately to your DuckDB database! 🚀
