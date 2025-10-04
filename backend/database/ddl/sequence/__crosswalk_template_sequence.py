# DuckDB sequence creation for crosswalk_template
import duckdb

con = duckdb.connect('/Users/deeahnuh/Documents/Repos/CrosswalkAArete/backend/database/crosswalk.duckdb')

# -------- create a sequence 
result = con.execute("CREATE SEQUENCE IF NOT EXISTS crosswalk_template_seq START 1 INCREMENT 1;")
print(result.fetchall())
result = con.execute("ALTER TABLE crosswalk_template ALTER COLUMN id SET DEFAULT nextval('crosswalk_template_seq');")
print(result.fetchall())
con.close()
