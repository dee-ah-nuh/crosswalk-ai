import duckdb 
import os 

from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.getenv("DUCKDB_PATH")
con = duckdb.connect(DB_PATH)

source_columns_ddl = """
CREATE TABLE IF NOT EXISTS source_columns (
    id INTEGER PRIMARY KEY,
    profile_id INTEGER,
    source_column VARCHAR NOT NULL,
    sample_values_json TEXT,
    inferred_type VARCHAR
);
"""

def create_source_columns_table(db_path=':memory:', sql_ddl=None):
    con = duckdb.connect(db_path)
    con.execute(source_columns_ddl)

    if sql_ddl:
        con.execute(sql_ddl)
        print("source_columns table created from provided SQL DDL.")
    return con

if __name__ == "__main__":
    db_path = os.getenv("DUCKDB_PATH", ":memory:")
    con = create_source_columns_table(db_path=db_path)
    print("source_columns table created in DuckDB database at:", db_path)
    con.close()
    