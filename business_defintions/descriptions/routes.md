# CrosswalkAI API Routes Documentation

## Overview
This document explains how the FastAPI backend routes work, specifically how user input from the UI gets processed and stored in DuckDB.

## Profile Management Routes

### Create Profile Endpoint

#### Route Definition
```python
@router.post("/profiles")
async def create_profile(
    name: str = Form(...),
    client_id: str = Form(""),
    db: Session = Depends(DuckDBClient.get_duckdb)
):
```

#### How It Works

**1. UI/Frontend Side:**
The user fills out a form in the web interface with:
- Profile name (required)
- Client ID (optional)


**2. HTTP Request:**
When the user submits the form, the frontend sends a POST request to:
```
POST /profiles
```

The data is sent as **form data** (not JSON), which looks like:
```
Content-Type: application/x-www-form-urlencoded

name=My%20Project&client_id=ACME_CORP
```

**3. FastAPI Processing:**

- **Route Decorator:** `@router.post("/profiles")` catches POST requests to `/profiles`
- **Parameters:**
  - `name: str = Form(...)` - Extracts the "name" from form data (required due to `...`)
  - `client_id: str = Form("")` - Extracts "client_id" from form data (defaults to empty string)
  - `db: Session = Depends(DuckDBClient.get_duckdb)` - Gets a database session

**4. Database Operations:**
```python
# Create a new SourceProfile object
profile = SourceProfile(
    name=name,
    client_id=client_id if client_id else None  # Convert empty string to None
)

# Add to database session
db.add(profile)

# Save changes to DuckDB
db.commit()

# Refresh to get the auto-generated ID
db.refresh(profile)
```

**5. Response:**
Returns JSON back to the frontend:
```json
{
  "id": 123,
  "name": "My Project", 
  "client_id": "ACME_CORP"
}
```

#### Key Points:
- **Form Data**: Uses `Form()` instead of JSON - typical for file uploads and simple forms
- **DuckDB**: Creates a new record in your DuckDB database
- **SQLAlchemy ORM**: Uses the `SourceProfile` model to interact with the database
- **Error Handling**: Catches exceptions and returns HTTP 500 errors if something goes wrong

---

### File Ingestion Endpoint

#### Route Definition
```python
@router.post("/profiles/{profile_id}/source/ingest-file")
async def ingest_file(
    profile_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(DuckDBClient.get_duckdb)
):
```

#### What It Does
This endpoint allows users to upload and process source files (like CSV or Excel files) for a specific profile.

#### Route Components:
- **`@router.post(...)`** - Creates a POST endpoint (for uploading/creating data)
- **`"/profiles/{profile_id}/source/ingest-file"`** - URL path pattern:
  - `/profiles/` - Base path for profile-related operations
  - `{profile_id}` - A path parameter that captures the profile ID from the URL
  - `/source/ingest-file` - The specific action being performed

#### Example Usage:
If you have a profile with ID `123`, you would make a POST request to:
```
POST /profiles/123/source/ingest-file
```

#### The Process:
1. Takes a `profile_id` (from the URL) and a file upload
2. Reads and parses the uploaded file (CSV/XLSX)
3. Extracts column names and sample data
4. Stores this information in the database as "source columns" for that profile
5. Marks the profile as having a physical file

This is typically used when users want to upload their source data files to analyze the structure and create mappings to a target data model.

---

## General Data Flow

### User Input → DuckDB Storage

**Summary:** Yes, user input from the UI → POST request → stored in DuckDB!

1. **User Interface**: User fills out forms or uploads files
2. **HTTP Request**: Frontend sends POST/GET/PUT requests to backend API
3. **FastAPI Routes**: Process the request, validate data, handle business logic
4. **SQLAlchemy ORM**: Interacts with database using Python objects
5. **DuckDB**: Stores the actual data persistently
6. **Response**: API returns JSON response back to frontend
7. **UI Update**: Frontend updates the user interface with the response

### Error Handling
- All routes include try/catch blocks
- Database errors return HTTP 500 status codes
- Validation errors return HTTP 400 status codes
- Missing resources return HTTP 404 status codes
- Detailed error messages are logged and returned to help with debugging

### Database Session Management
- Uses dependency injection with `Depends(DuckDBClient.get_duckdb)`
- Automatically handles database connection lifecycle
- Ensures proper cleanup of database resources
- Supports transaction rollback on errors
