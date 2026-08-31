from pathlib import Path

import duckdb


class Database:
    def __init__(self,path:str|Path="data_store/market_lab.duckdb"): self.path=str(path); Path(path).parent.mkdir(parents=True,exist_ok=True)
    def connect(self): return duckdb.connect(self.path)
    def initialise(self)->None:
        with self.connect() as c:
            c.execute("CREATE TABLE IF NOT EXISTS records(kind VARCHAR, record_id VARCHAR PRIMARY KEY, timestamp TIMESTAMP, payload JSON)")
