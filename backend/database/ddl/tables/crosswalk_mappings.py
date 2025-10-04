import duckdb
import os 

from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.getenv("DUCKDB_PATH")
con = duckdb.connect(DB_PATH)

crosswalk_mappings_ddl = """
CREATE TABLE IF NOT EXISTS crosswalk_mappings (
    id INTEGER PRIMARY KEY,
    profile_id INTEGER,
    source_column_id INTEGER,
    model_table VARCHAR NOT NULL,
    model_column VARCHAR NOT NULL,
    is_custom_field BOOLEAN DEFAULT FALSE,
    custom_field_name VARCHAR,
    transform_expression TEXT,
    notes TEXT
);
"""

def create_crosswalk_mappings_table(db_path=':memory:', sql_ddl=None):
    con = duckdb.connect(db_path)
    con.execute(crosswalk_mappings_ddl)

    if sql_ddl:
        con.execute(sql_ddl)
        print("crosswalk_mappings table created from provided SQL DDL.")
    return con

# if __name__ == "__main__":
#     db_path = os.getenv("DUCKDB_PATH", ":memory:")
#     con = create_crosswalk_mappings_table(db_path=db_path)
#     print("crosswalk_mappings table created in DuckDB database at:", db_path)
#     con.close()