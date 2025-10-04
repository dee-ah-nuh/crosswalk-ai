# DuckDB sequence creation for source_profiles table
import duckdb
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv("DUCKDB_PATH")
con = duckdb.connect(DB_PATH)

# -------- create a sequence 
result = con.execute("CREATE SEQUENCE IF NOT EXISTS crosswalk_mappings_seq START 1 INCREMENT 1;")
print(result.fetchall())
result = con.execute("ALTER TABLE crosswalk_mappings ALTER COLUMN id SET DEFAULT nextval('crosswalk_mappings_seq');")
print(result.fetchall())
con.close()


