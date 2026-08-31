import json

from pydantic import BaseModel

from database.db import Database


class Repository:
    def __init__(self,db:Database):self.db=db;db.initialise()
    def append_immutable(self,kind:str,record:BaseModel,record_id:str,timestamp)->None:
        with self.db.connect() as c:c.execute("INSERT INTO records VALUES (?,?,?,?)",[kind,record_id,timestamp,json.dumps(record.model_dump(mode="json"))])
    def list(self,kind:str):
        with self.db.connect() as c:return c.execute("SELECT payload FROM records WHERE kind=? ORDER BY timestamp",[kind]).fetchall()
