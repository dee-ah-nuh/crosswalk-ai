import duckdb 
import os 

duckdb_path = os.getenv("DUCKDB_PATH", "/Users/deeahnuh/Documents/Repos/CrosswalkAArete/backend/database/crosswalk.duckdb")

crosswalk_template_excel_ddl = """
CREATE TABLE IF NOT EXISTS crosswalk_template (
    id INTEGER PRIMARY KEY,
    client_id VARCHAR(100) NOT NULL,
    source_column_order INTEGER,
    source_column_name VARCHAR(255) NOT NULL,
    file_group_name VARCHAR(100) NOT NULL,
    mcdm_column_name VARCHAR(255),
    in_model VARCHAR(10) DEFAULT 'Y',
    mcdm_table VARCHAR(100),
    custom_field_type VARCHAR(50),
    data_profile_info TEXT,
    profile_column_2 TEXT,
    profile_column_3 TEXT,
    profile_column_4 TEXT,
    profile_column_5 TEXT,
    profile_column_6 TEXT,
    source_column_formatting TEXT,
    skipped_flag BOOLEAN DEFAULT FALSE,
    additional_field_1 TEXT,
    additional_field_2 TEXT,
    additional_field_3 TEXT,
    additional_field_4 TEXT,
    additional_field_5 TEXT,
    additional_field_6 TEXT,
    additional_field_7 TEXT,
    additional_field_8 TEXT,
    target_tables TEXT,
    provider_file_group VARCHAR,
    is_multi_table BOOLEAN DEFAULT FALSE,
    crosswalk_version VARCHAR DEFAULT '1.0',
    parent_mapping_id INTEGER,
    reuse_from_client VARCHAR,
    version_notes TEXT,
    inferred_data_type VARCHAR,
    custom_data_type VARCHAR,
    data_type_source VARCHAR DEFAULT 'INFERRED',
    source_file_name VARCHAR,
    join_key_column VARCHAR,
    join_table VARCHAR,
    join_type VARCHAR DEFAULT 'INNER',
    mcs_review_required BOOLEAN DEFAULT FALSE,
    mcs_review_notes TEXT,
    mcs_review_status VARCHAR DEFAULT 'PENDING',
    mcs_reviewer VARCHAR,
    mcs_review_date TIMESTAMP,
    complexity_score INTEGER DEFAULT 1,
    business_priority VARCHAR DEFAULT 'MEDIUM',
    completion_status VARCHAR DEFAULT 'DRAFT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def create_crosswalk_template_excel_table(db_path=':memory:', sql_ddl=None):
    con = duckdb.connect(db_path)
    con.execute(crosswalk_template_excel_ddl)

    if sql_ddl:
        con.execute(sql_ddl)
        print("Crosswalk template table created from provided SQL DDL.")
    return con

if __name__ == "__main__":
    con = create_crosswalk_template_excel_table(db_path=duckdb_path)
    con.execute("SELECT * FROM crosswalk_template LIMIT 5;")
    result = con.fetchall()
    print(result)
    print("Crosswalk template table created in DuckDB database at:", duckdb_path)
    con.close()