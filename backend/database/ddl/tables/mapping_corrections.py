import duckdb 
import os 

duckdb_path = os.getenv("DUCKDB_PATH", ":memory:")

mapping_corrections_ddl = """
CREATE TABLE IF NOT EXISTS mapping_corrections (
	source_column TEXT,
	correct_target_table TEXT,
	correct_target_column TEXT,
	incorrect_suggestion TEXT,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def create_mapping_corrections_table(db_path=':memory:', sql_ddl=None):
    con = duckdb.connect(db_path)
    con.execute(mapping_corrections_ddl)

    if sql_ddl:
        con.execute(sql_ddl)
        print("mapping_corrections table created from provided SQL DDL.")
    return con

# if __name__ == "__main__":
#     db_path = os.getenv("DUCKDB_PATH", ":memory:")
#     con = create_mapping_corrections_table(db_path=db_path)
#     print("mapping_corrections table created in DuckDB database at:", db_path)
#     con.close()