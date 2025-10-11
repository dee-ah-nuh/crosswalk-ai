# # data/_create_all_tables.py
# import os

# # Define the final database file name
# DUCKDB_FILENAME = "crosswalk.duckdb" 

# # Use path manipulation to locate the file two directories above the script's location.
# # os.path.dirname(__file__) is the 'data/' directory.
# # os.path.join(..., '..') moves up one level (to the root).
# # os.path.join(..., '..') moves up a *second* level (not applicable here, the root is one level up).
# # A simpler way is to rely on the current working directory, 
# # but using the script's location is safer in CI environments.

# # REVISED PATH CALCULATION:
# # The repository root is '..' from the 'data/' folder.
# # The database file should be in the root directory.

# # Calculate the path from the script's location (data/):
# db_path = os.path.join(os.path.dirname(__file__), '..', DUCKDB_FILENAME)

# # --- ORIGINAL CODE (from the user's local setup) ---
# # db_path = os.getenv("DUCKDB_PATH", "/Users/deeahnuh/Documents/Repos/CrosswalkAArete/backend/database/crosswalk.duckdb")
# # --- END ORIGINAL CODE ---

# print(f"Building DuckDB database at: {db_path}")

# ... (Imports and function calls remain the same, using the new db_path) ...


import os

# Calculate CI-friendly database path
# This works both locally and in GitHub Actions
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up from tables/ -> ddl/ -> database/ -> backend/ -> root/
db_directory = os.path.join(script_dir, '..', '..', '..', '..')
db_path = os.getenv("DUCKDB_PATH", os.path.join(db_directory, "backend", "database", "crosswalk.duckdb"))

# Ensure the directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

print(f"Using DuckDB path: {db_path}")

from create_pi20_data_model import create_data_model #type: ignore
from create_crosswalk_excel import crosswalk_template_excel_ddl #type: ignore
from create_source_profiles import create_source_profiles_table #type: ignore
from create_source_columns import create_source_columns_table #type: ignore
from crosswalk_mappings import create_crosswalk_mappings_table #type: ignore
from create_regex_rules import create_regex_rules_table #type: ignore
from mapping_corrections import create_mapping_corrections_table #type: ignore

# Create all tables
create_data_model(db_path=db_path)
create_source_profiles_table(db_path=db_path)
create_source_columns_table(db_path=db_path)
create_crosswalk_mappings_table(db_path=db_path)
create_regex_rules_table(db_path=db_path)
create_mapping_corrections_table(db_path=db_path)

print(f"All tables created in DuckDB database at: {db_path}")