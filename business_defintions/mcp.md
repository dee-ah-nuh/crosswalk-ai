# CrosswalkAI MCP Server

## Overview

This MCP (Model Context Protocol) server exposes the complete functionality of your CrosswalkAI healthcare data engineering application to AI agents. It allows AI assistants to interact with your crosswalk mapping system, create profiles, suggest mappings, and export results.

## Features

### 🔧 Tools (Functions AI Agents Can Call)
- **Profile Management**: Create, list, and manage source data profiles
- **Data Model Operations**: Search and explore PI20 data model fields
- **Auto-Mapping**: Get AI-powered mapping suggestions with confidence scores
- **Crosswalk Operations**: Create, update, and manage field mappings
- **Export Functions**: Export mappings as CSV, JSON, or SQL scripts
- **Snowflake Integration**: Generate deployment scripts for Snowflake
- **System Monitoring**: Get health stats and system information

### 📚 Resources (Data AI Agents Can Read)
- `crosswalk://profiles/all` - All source profiles
- `crosswalk://pi20/fields` - Complete PI20 data model
- `crosswalk://mappings/{profile_id}` - Mappings for specific profiles
- `crosswalk://system/stats` - System health and statistics

### 💬 Prompts (Guided Interactions)
- `analyze_healthcare_data` - Step-by-step data analysis guidance
- `troubleshoot_mapping_issues` - Help with mapping problems

## Setup

### 1. Create Virtual Environment
```bash
python3.10 -m venv .mcp
source .mcp/bin/activate
```

### 2. Install Dependencies
```bash
pip install mcp fastmcp httpx duckdb sqlalchemy fuzzywuzzy pandas numpy scikit-learn pydantic
```

### 3. Test Installation
```bash
python test_mcp_server.py
```

## Running the Server

### Option 1: Using the startup script
```bash
./start_mcp_server.sh
```

### Option 2: Manual start
```bash
source .mcp/bin/activate
python crosswalk_ai_mcp_server.py
```

## Usage Examples

### Example 1: Creating a New Profile and Mapping
```python
# AI agent would call these tools:
create_profile(name="Hospital Claims Data", client_id="ACME_HEALTH")
search_pi20_fields(search_term="patient", limit=5)
suggest_mappings([{"column_name": "PATIENT_ID", "sample_values": ["P123456", "P789012"]}])
create_crosswalk_mapping(profile_id=1, source_column_id=1, target_table="patient", target_column="patient_id")
```

### Example 2: Exporting Mappings
```python
# Export as JSON
export_crosswalk_json(profile_id=1)

# Export as CSV  
export_crosswalk_csv(profile_id=1)

# Generate Snowflake SQL
generate_snowflake_sql(profile_id=1, config={"database": "ANALYTICS", "schema": "STAGING"})
```

### Example 3: System Monitoring
```python
# Get comprehensive system statistics
get_system_stats()

# List all profiles
list_profiles()

# Get PI20 field details
get_pi20_field_details("patient_id")
```

## Integration with MCP Clients

This server works with any MCP-compatible client, including:

- **Claude Desktop** (Anthropic)
- **VS Code with MCP extension**
- **Custom MCP clients**
- **Command-line MCP tools**

### Client Configuration Example
```json
{
  "mcpServers": {
    "crosswalk-ai": {
      "command": "python",
      "args": ["/path/to/crosswalk_ai_mcp_server.py"],
      "cwd": "/path/to/CrosswalkAI"
    }
  }
}
```

## Architecture

The MCP server acts as a bridge between AI agents and your CrosswalkAI backend:

```
AI Agent ←→ MCP Protocol ←→ CrosswalkAI MCP Server ←→ DuckDB Database
                                     ↓
                              Backend Services:
                              • Auto Mapper
                              • File Parser  
                              • Export Service
                              • DSL Engine
```

## Error Handling

The server includes comprehensive error handling:
- Database connection failures are gracefully handled
- Missing dependencies are reported clearly
- Invalid parameters return helpful error messages
- All errors are logged for debugging

## Development

### File Structure
- `crosswalk_ai_mcp_server.py` - Main MCP server implementation
- `test_mcp_server.py` - Test suite for basic functionality
- `start_mcp_server.sh` - Startup script
- `.mcp/` - Virtual environment (ignored in git)

### Adding New Tools
To add new functionality:

1. Define a new tool function with the `@mcp.tool()` decorator
2. Add proper type hints and docstring
3. Handle errors gracefully
4. Test the new functionality

### Adding New Resources
To expose new data:

1. Define a resource function with `@mcp.resource("uri://path")`
2. Return JSON-formatted string
3. Handle errors and edge cases

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the `.mcp` environment is activated and dependencies are installed
2. **Database Connection**: Verify the DuckDB file exists and is accessible
3. **Port Conflicts**: The server uses default MCP ports; check for conflicts

### Debugging
- Enable debug logging by setting log level to DEBUG
- Check the database connection with `get_system_stats()`
- Verify backend services are available

## Security Considerations

- The server runs locally and doesn't expose external ports by default
- Database access is read/write - ensure proper file permissions
- Consider authentication for production deployments

## Performance

- Database queries are optimized for typical workloads
- Large result sets are paginated where appropriate
- Connection pooling is handled by SQLAlchemy
- Memory usage is optimized for typical profile sizes

## Contributing

To contribute to the MCP server:

1. Test changes with `python test_mcp_server.py`
2. Ensure all tools have proper error handling
3. Add documentation for new features
4. Follow the existing code structure and patterns
