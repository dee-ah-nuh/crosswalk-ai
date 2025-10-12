import duckdb 
import os

from dotenv import load_dotenv
load_dotenv()

# DDL definition (no connection here - connection happens in the function)
source_profiles_ddl = """
CREATE TABLE IF NOT EXISTS source_profiles (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    client_id VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    has_physical_file BOOLEAN DEFAULT FALSE,
    raw_table_name VARCHAR
);
"""

def create_source_profiles_table(db_path=':memory:', sql_ddl=None):
    con = duckdb.connect(db_path)
    con.execute(source_profiles_ddl)

    if sql_ddl:
        con.execute(sql_ddl)
        print("source_profiles table created from provided SQL DDL.")
    return con

# if __name__ == "__main__":
#     db_path = os.getenv("DUCKDB_PATH", ":memory:")
#     con = create_source_profiles_table(db_path=db_path)
#     print("source_profiles table created in DuckDB database at:", db_path)
#     con.close()
    