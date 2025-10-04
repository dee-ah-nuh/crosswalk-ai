import os

# Set your DuckDB path here
db_path = os.getenv("DUCKDB_PATH", "/Users/deeahnuh/Documents/Repos/CrosswalkAArete/backend/database/crosswalk.duckdb")
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