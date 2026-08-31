from pathlib import Path

import pandas as pd


class FeatureStore:
    def __init__(self,root:str|Path="data_store/features"):self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
    def write(self,frame:pd.DataFrame,version:str)->Path:
        path=self.root/f"{version}.parquet";frame.to_parquet(path,index=False);return path
    def read(self,version:str)->pd.DataFrame:return pd.read_parquet(self.root/f"{version}.parquet")
