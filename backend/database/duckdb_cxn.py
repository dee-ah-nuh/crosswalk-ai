# ----- IMPORTS -----
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import duckdb

load_dotenv()

db_path = os.getenv("DUCKDB_PATH", ":memory:")
engine = create_engine(f"duckdb:///{db_path}")

from sqlalchemy.orm import sessionmaker
DuckDBSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DuckDBClient:
    "------- Function definitions for DuckDBClient -------"

    "------- Connect to duckdb database -------"
    def __init__(self, db_path):
        self.db_path = db_path
        self.con = duckdb.connect(db_path)
    "------- Get SQLAlchemy engine -------"
    def get_engine(self):
        return create_engine(f"duckdb:///{self.db_path}")
    
    " ------ Dependency to get DuckDB session -------"
    @staticmethod
    def get_duckdb():
        """Dependency to get DuckDB session"""
        db = DuckDBSessionLocal()
        try:
            yield db
        finally:
            db.close()
        
    "------- Get client -------"
    def get_client(self):
        return self.con
    "------- Run query -------"
    def run_query(self, q):
        return self.con.execute(q).fetchall()
    "------- Close connection -------"
    def close(self):
        self.con.close()




# # Tests:
# if __name__=="__main__":
#     db_path=os.getenv("DUCKDB_PATH", ":memory:")
#     client=DuckDBClient(db_path)

#     print("DuckDB Client connected to:",db_path)
#     client.run_query("CREATE TABLE if not exists test (id INTEGER, name VARCHAR);")
#     client.run_query("INSERT INTO test VALUES (1, 'Goose'), (2, 'Noma');")
#     results=client.run_query("SELECT * FROM test;")

#     print(results)
#     client.close()
