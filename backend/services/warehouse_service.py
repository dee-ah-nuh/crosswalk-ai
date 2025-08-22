"""
Warehouse service for connecting to data warehouses and fetching sample data.
"""

import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from models import WarehouseConfig

class WarehouseService:
    """Service for warehouse operations"""
    
    @staticmethod
    def is_warehouse_enabled() -> bool:
        """Check if warehouse connectivity is enabled via environment variables"""
        return os.getenv("WAREHOUSE_ENABLED", "false").lower() == "true"
    
    @staticmethod
    def get_warehouse_config(db: Session, profile_id: int) -> Optional[WarehouseConfig]:
        """Get warehouse configuration for a profile"""
        return db.query(WarehouseConfig).filter(
            WarehouseConfig.profile_id == profile_id,
            WarehouseConfig.enabled == True
        ).first()
    
    @staticmethod
    async def fetch_sample_data(db: Session, profile_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch sample data from warehouse using stored procedure.
        
        Args:
            db: Database session
            profile_id: Profile ID
            limit: Maximum number of rows to fetch
            
        Returns:
            List of dictionaries representing sample rows
        """
        if not WarehouseService.is_warehouse_enabled():
            raise ValueError("Warehouse connectivity is not enabled")
        
        config = WarehouseService.get_warehouse_config(db, profile_id)
        if not config:
            raise ValueError("No warehouse configuration found for this profile")
        
        try:
            # Import snowflake connector only if needed
            import snowflake.connector
            
            # Get connection parameters from environment
            connection_params = {
                'account': os.getenv("SNOWFLAKE_ACCOUNT", config.account),
                'user': os.getenv("SNOWFLAKE_USER", config.user),
                'password': os.getenv("SNOWFLAKE_PASSWORD"),
                'role': os.getenv("SNOWFLAKE_ROLE", config.role),
                'warehouse': os.getenv("SNOWFLAKE_WAREHOUSE", config.warehouse),
                'database': os.getenv("SNOWFLAKE_DATABASE", config.database),
                'schema': os.getenv("SNOWFLAKE_SCHEMA", config.schema)
            }
            
            # Remove None values
            connection_params = {k: v for k, v in connection_params.items() if v is not None}
            
            # Connect to Snowflake
            conn = snowflake.connector.connect(**connection_params)
            cursor = conn.cursor()
            
            # Get the profile to find raw_table_name
            from models import SourceProfile
            profile = db.query(SourceProfile).filter(SourceProfile.id == profile_id).first()
            if not profile or not profile.raw_table_name:
                raise ValueError("No raw table name specified for this profile")
            
            # Prepare stored procedure call
            sp_template = os.getenv("SP_TEMPLATE", config.stored_procedure_call)
            if not sp_template:
                raise ValueError("No stored procedure template configured")
            
            # Replace template variables
            sp_call = sp_template.replace("{RAW_TABLE}", profile.raw_table_name)
            sp_call = sp_call.replace("{LIMIT}", str(limit))
            
            # Execute stored procedure
            cursor.execute(sp_call)
            
            # Fetch results
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            sample_data = []
            for row in rows:
                sample_data.append(dict(zip(columns, row)))
            
            cursor.close()
            conn.close()
            
            return sample_data
            
        except ImportError:
            raise ValueError("Snowflake connector not available. Install snowflake-connector-python to enable warehouse connectivity.")
        except Exception as e:
            raise ValueError(f"Error fetching sample data from warehouse: {str(e)}")
    
    @staticmethod
    def test_warehouse_connection(db: Session, profile_id: int) -> Dict[str, Any]:
        """Test warehouse connection for a profile"""
        try:
            config = WarehouseService.get_warehouse_config(db, profile_id)
            if not config:
                return {"success": False, "message": "No warehouse configuration found"}
            
            # Try to establish connection (without executing queries)
            import snowflake.connector
            
            connection_params = {
                'account': os.getenv("SNOWFLAKE_ACCOUNT", config.account),
                'user': os.getenv("SNOWFLAKE_USER", config.user),
                'password': os.getenv("SNOWFLAKE_PASSWORD"),
                'role': os.getenv("SNOWFLAKE_ROLE", config.role),
                'warehouse': os.getenv("SNOWFLAKE_WAREHOUSE", config.warehouse),
                'database': os.getenv("SNOWFLAKE_DATABASE", config.database),
                'schema': os.getenv("SNOWFLAKE_SCHEMA", config.schema)
            }
            
            # Remove None values
            connection_params = {k: v for k, v in connection_params.items() if v is not None}
            
            conn = snowflake.connector.connect(**connection_params)
            conn.close()
            
            return {"success": True, "message": "Connection successful"}
            
        except ImportError:
            return {"success": False, "message": "Snowflake connector not available"}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {str(e)}"}
