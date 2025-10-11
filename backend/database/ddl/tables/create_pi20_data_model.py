import pandas as pd 
import duckdb
import os 

#env variable for db path
db_path = os.getenv("DUCKDB_PATH", "/Users/deeahnuh/Documents/Repos/CrosswalkAArete/backend/database/crosswalk.duckdb")
print(f"Using DuckDB path: {db_path}")

# Python Script to Create and Load Data Model Into Memory
pi20_data_model_csv = '/Users/deeahnuh/Documents/Repos/CrosswalkAArete/business_defintions/pi20_data_model.csv'

create_pi20_data_model = """
CREATE TABLE IF NOT EXISTS pi20_data_model (
  IN_CROSSWALK VARCHAR,
  TABLE_NAME VARCHAR,
  COLUMN_NAME VARCHAR,
  COLUMN_TYPE VARCHAR,
  COLUMN_ORDER INTEGER,
  COLUMN_COMMENT VARCHAR,
  TABLE_CREATION_ORDER INTEGER,
  IS_MANDATORY BOOLEAN,
  MANDATORY_PROV_TYPE VARCHAR,
  MCDM_MASKING_TYPE VARCHAR,
  IN_EDITS BOOLEAN,
  KEY VARCHAR
);"""

def insert_pi20_data_model_from_csv(con, csv_path):
    pi_data_model = pd.read_csv(csv_path)
    con.execute("TRUNCATE TABLE pi20_data_model;")
    con.register('pi_data_model_df', pi_data_model)
    con.execute("INSERT INTO pi20_data_model SELECT * FROM pi_data_model_df")

def create_data_model(db_path=':memory:', sql_ddl=None):
    con = duckdb.connect(db_path)
    con.execute(create_pi20_data_model)

    if sql_ddl:
        con.execute(sql_ddl)
        print("Data model created from provided SQL DDL.")
    return con

# if __name__ == "__main__":
#     con = create_data_model(db_path=db_path)
#     insert_pi20_data_model_from_csv(con, pi20_data_model_csv)
#     print("PI20 Data Model loaded into DuckDB.")


#     result = con.execute("SELECT IN_CROSSWALK, TABLE_NAME FROM pi20_data_model LIMIT 1;").fetchall()
#     for row in result:
#         print(row)
#     con.close()


