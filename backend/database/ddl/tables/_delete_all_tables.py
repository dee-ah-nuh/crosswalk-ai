import os
import duckdb 

crosswalk_mappings = "DROP TABLE IF EXISTS CROSSWALK_MAPPINGS;"
source_columns = "DROP TABLE IF EXISTS SOURCE_COLUMNS;"
source_profiles = "DROP TABLE IF EXISTS SOURCE_PROFILES;"


DB_PATH = os.getenv("DUCKDB_PATH")
con = duckdb.connect(DB_PATH)


con.execute(crosswalk_mappings) 
print("Dropped CROSSWALK_MAPPINGS table if it existed.")

con.execute(source_columns)
print("Dropped SOURCE_COLUMNS table if it existed.")
con.execute(source_profiles)

print("Dropped SOURCE_PROFILES table if it existed.")
con.close()

