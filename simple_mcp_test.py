#!/usr/bin/env python3
"""
CrosswalkAI MCP Server with Real Database
=========================================

MCP server that connects to your actual DuckDB database and PI20 data model.
"""

import os
import sys
import json
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def main():
    """Initialize MCP server with real database connection"""
    
    print("🚀 CrosswalkAI MCP Server - Real Database")
    print("=" * 45)
    
    # Database path
    db_path = "backend/database/crosswalk.duckdb"
    print(f"📁 Database path: {db_path}")
    
    try:
        from fastmcp import FastMCP #type:ignore
        import duckdb
        print("✅ FastMCP and DuckDB imported")
        
        # Check if database exists
        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            print("Make sure your backend is set up and database is created")
            return False
        
        # Create MCP server
        mcp = FastMCP("CrosswalkAI Real Database Server")
        print("✅ MCP server created")
        
        # Test database connection
        try:
            conn = duckdb.connect(db_path)
            result = conn.execute("SELECT COUNT(*) FROM pi20_data_model").fetchone()
            pi20_count = result[0] if result else 0
            conn.close()
            print(f"✅ Database connected - {pi20_count} PI20 fields available")
        except Exception as e:
            print(f"⚠️  Database connection issue: {e}")
            pi20_count = 0
        
        # Tool to search actual PI20 data model
        @mcp.tool()
        def search_pi20_fields(search_term: str, limit: int = 10) -> list:
            """Search PI20 data model fields by name or description"""
            try:
                conn = duckdb.connect(db_path)
                query = """
                    SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT, IS_MANDATORY
                    FROM pi20_data_model
                    WHERE COLUMN_NAME ILIKE ? OR COLUMN_COMMENT ILIKE ?
                    ORDER BY COLUMN_NAME
                    LIMIT ?
                """
                search_pattern = f"%{search_term}%"
                result = conn.execute(query, [search_pattern, search_pattern, limit]).fetchall()
                conn.close()
                
                fields = []
                for row in result:
                    fields.append({
                        "table": row[0],
                        "column": row[1], 
                        "type": row[2],
                        "description": row[3],
                        "mandatory": row[4]
                    })
                return fields
            except Exception as e:
                return [{"error": str(e)}]
        
        # Tool to get intelligent mapping suggestions using real data
        @mcp.tool()
        def map_columns_intelligent(columns: list) -> dict:
            """Map healthcare columns to real PI20 fields with intelligent matching"""
            try:
                conn = duckdb.connect(db_path)
                # Get all PI20 fields for matching
                all_fields = conn.execute("SELECT TABLE_NAME, COLUMN_NAME, COLUMN_COMMENT FROM pi20_data_model").fetchall()
                conn.close()
                
                results = {}
                for col in columns:
                    col_lower = col.lower()
                    best_match = None
                    best_confidence = 0
                    
                    # Search through actual PI20 fields
                    for table, pi20_col, description in all_fields:
                        pi20_col_lower = pi20_col.lower()
                        desc_lower = (description or "").lower()
                        
                        confidence = 0
                        
                        # Exact match gets highest confidence
                        if col_lower == pi20_col_lower:
                            confidence = 98
                        # Contains match in column name
                        elif col_lower in pi20_col_lower or pi20_col_lower in col_lower:
                            confidence = 85
                        # Check description match
                        elif any(word in desc_lower for word in col_lower.split('_')):
                            confidence = 70
                        # Pattern matching
                        elif ('patient' in col_lower or 'member' in col_lower) and 'patient' in pi20_col_lower:
                            confidence = 90
                        elif 'date' in col_lower and 'date' in pi20_col_lower:
                            confidence = 85
                        elif ('amount' in col_lower or 'cost' in col_lower) and ('amount' in pi20_col_lower or 'cost' in pi20_col_lower):
                            confidence = 90
                        
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = {
                                "target_table": table,
                                "target_column": pi20_col,
                                "confidence": confidence,
                                "description": description or "No description"
                            }
                    
                    results[col] = best_match if best_match else {
                        "target_table": "unknown",
                        "target_column": "unknown_field", 
                        "confidence": 30,
                        "description": "No suitable match found"
                    }
                
                return {"input_columns": columns, "mappings": results}
            except Exception as e:
                return {"error": str(e)}
        
        # Tool to list all available PI20 tables
        @mcp.tool()
        def list_pi20_tables() -> list:
            """List all tables in the PI20 data model"""
            try:
                conn = duckdb.connect(db_path)
                result = conn.execute("""
                    SELECT TABLE_NAME, COUNT(*) as field_count
                    FROM pi20_data_model
                    GROUP BY TABLE_NAME
                    ORDER BY TABLE_NAME
                """).fetchall()
                conn.close()
                
                tables = []
                for row in result:
                    tables.append({
                        "table_name": row[0],
                        "field_count": row[1]
                    })
                return tables
            except Exception as e:
                return [{"error": str(e)}]
        
        print("✅ Tool registered")
        
        # Add prompts for AI agents to ask questions
        @mcp.prompt()
        def analyze_healthcare_data(data_description: str) -> str:
            """
            Guide for analyzing healthcare data and creating mappings.
            
            Args:
                data_description: Description of the healthcare data to analyze
            """
            return f"""I need help analyzing this healthcare data: {data_description}

Please help me:
1. Identify the column types (patient IDs, dates, amounts, codes, etc.)
2. Suggest appropriate PI20 mappings using the map_columns tool
3. Assess mapping confidence and suggest improvements
4. Point out any potential data quality issues

Available tools:
- map_columns(columns) - Maps a list of column names to PI20 fields

Let's start by examining the column names. What patterns do you see?"""

        @mcp.prompt()
        def mapping_questions(column_name: str) -> str:
            """
            Ask specific questions about mapping a single column.
            
            Args:
                column_name: Name of the column to get mapping questions for
            """
            return f"""I have a column named "{column_name}" and need to map it properly.

Can you help me answer these questions:
1. What type of healthcare data does this column likely contain?
2. What PI20 field would be the best mapping target?
3. What's the confidence level of this mapping?
4. Are there any alternative mapping options I should consider?
5. What data validation rules should I apply?

Use the map_columns tool to get suggestions, then provide your analysis."""

        @mcp.prompt()
        def troubleshoot_mapping(issue_description: str) -> str:
            """
            Help troubleshoot mapping issues and data problems.
            
            Args:
                issue_description: Description of the mapping issue or problem
            """
            return f"""I'm having this mapping issue: {issue_description}

Please help me troubleshoot:
1. Analyze what might be causing this problem
2. Suggest alternative mapping approaches
3. Recommend data quality checks
4. Provide step-by-step resolution steps

Common issues to consider:
- Column name ambiguity
- Data type mismatches  
- Missing or null values
- Format inconsistencies
- Business rule conflicts

What do you think is the best approach to resolve this?"""

        print("✅ Prompts registered")
        
        # Resource with real PI20 data model
        @mcp.resource("crosswalk://pi20-fields")
        def pi20_fields_resource() -> str:
            """Resource exposing actual PI20 data model fields"""
            try:
                conn = duckdb.connect(db_path)
                result = conn.execute("""
                    SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT, IS_MANDATORY
                    FROM pi20_data_model
                    ORDER BY TABLE_NAME, COLUMN_NAME
                    LIMIT 50
                """).fetchall()
                conn.close()
                
                fields = []
                for row in result:
                    fields.append({
                        "table": row[0],
                        "column": row[1],
                        "type": row[2], 
                        "description": row[3],
                        "mandatory": bool(row[4])
                    })
                
                return json.dumps({
                    "pi20_data_model": fields,
                    "total_fields_shown": len(fields),
                    "note": "Use search_pi20_fields() tool to find specific fields"
                }, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)})
        
        print("✅ Resource registered")
        
        # Test with real database
        test_columns = ["PATIENT_ID", "SERVICE_DATE", "CLAIM_AMOUNT"]
        print(f"\n🧪 Testing with real database using columns: {test_columns}")
        
        # Test PI20 search directly
        print(f"\n🔍 Searching PI20 fields for 'patient':")
        try:
            conn = duckdb.connect(db_path)
            query = """
                SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT
                FROM pi20_data_model
                WHERE COLUMN_NAME ILIKE '%patient%' OR COLUMN_COMMENT ILIKE '%patient%'
                ORDER BY COLUMN_NAME
                LIMIT 3
            """
            result = conn.execute(query).fetchall()
            conn.close()
            
            for row in result:
                table, column, col_type, description = row
                print(f"   📋 {table}.{column} ({col_type}) - {description or 'No description'}")
        except Exception as e:
            print(f"   ❌ Search error: {e}")
        
        # Test intelligent mapping directly
        print(f"\n🎯 Intelligent mapping results:")
        try:
            conn = duckdb.connect(db_path)
            all_fields = conn.execute("SELECT TABLE_NAME, COLUMN_NAME, COLUMN_COMMENT FROM pi20_data_model").fetchall()
            conn.close()
            
            for col in test_columns:
                col_lower = col.lower()
                best_match = None
                best_confidence = 0
                
                # Search through actual PI20 fields
                for table, pi20_col, description in all_fields:
                    pi20_col_lower = pi20_col.lower()
                    desc_lower = (description or "").lower()
                    
                    confidence = 0
                    
                    # Exact match gets highest confidence
                    if col_lower == pi20_col_lower:
                        confidence = 98
                    # Contains match in column name
                    elif col_lower in pi20_col_lower or pi20_col_lower in col_lower:
                        confidence = 85
                    # Pattern matching
                    elif ('patient' in col_lower or 'member' in col_lower) and 'patient' in pi20_col_lower:
                        confidence = 90
                    elif 'date' in col_lower and 'date' in pi20_col_lower:
                        confidence = 85
                    elif ('amount' in col_lower or 'cost' in col_lower) and ('amount' in pi20_col_lower or 'cost' in pi20_col_lower):
                        confidence = 90
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = {
                            "target_table": table,
                            "target_column": pi20_col,
                            "confidence": confidence,
                            "description": description or "No description"
                        }
                
                if best_match:
                    confidence = best_match['confidence']
                    emoji = "🟢" if confidence >= 85 else "🟡" if confidence >= 70 else "🔴"
                    print(f"   {emoji} {col:<15} -> {best_match['target_table']}.{best_match['target_column']:<20} ({confidence}%)")
                    print(f"      💡 {best_match['description']}")
                else:
                    print(f"   🔴 {col:<15} -> No suitable match found")
        except Exception as e:
            print(f"   ❌ Mapping error: {e}")
        
        # Test table listing
        print(f"\n📊 Available PI20 tables:")
        try:
            conn = duckdb.connect(db_path)
            result = conn.execute("""
                SELECT TABLE_NAME, COUNT(*) as field_count
                FROM pi20_data_model
                GROUP BY TABLE_NAME
                ORDER BY TABLE_NAME
                LIMIT 5
            """).fetchall()
            conn.close()
            
            for row in result:
                table_name, field_count = row
                print(f"   📁 {table_name} ({field_count} fields)")
        except Exception as e:
            print(f"   ❌ Table listing error: {e}")
        
        print(f"\n✅ MCP server with real database test completed!")
        print(f"🔗 Server ready to accept your data and provide real mappings!")
        
        # Run the MCP server for client connections
        print(f"\n🚀 Starting MCP server for client connections...")
        mcp.run()
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: source .mcp/bin/activate")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()
