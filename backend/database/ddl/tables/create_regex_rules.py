import duckdb 
import os 

duckdb_path = os.getenv("DUCKDB_PATH", ":memory:")

regex_rules_ddl = """
CREATE TABLE IF NOT EXISTS regex_rules (
    source_column_id INTEGER NOT NULL,
    rule_name VARCHAR,
    pattern TEXT,
    flags VARCHAR,
    description TEXT
);
"""

def create_regex_rules_table(db_path=':memory:', sql_ddl=None):
    con = duckdb.connect(db_path)
    con.execute(regex_rules_ddl)

    if sql_ddl:
        con.execute(sql_ddl)
        print("regex_rules table created from provided SQL DDL.")
    return con

if __name__ == "__main__":
    db_path = os.getenv("DUCKDB_PATH", ":memory:")
    con = create_regex_rules_table(db_path=db_path)
    print("regex_rules table created in DuckDB database at:", db_path)
    con.close()

