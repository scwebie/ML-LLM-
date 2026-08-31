from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Fold: train_index:pd.Index; validation_index:pd.Index; train_end:pd.Timestamp; validation_start:pd.Timestamp
def expanding_window_splits(frame:pd.DataFrame,min_train_years:int=3,validation_years:int=1,date_column:str="timestamp")->list[Fold]:
    dates=pd.to_datetime(frame[date_column]); years=sorted(dates.dt.year.unique()); folds=[]
    for i in range(min_train_years,len(years)):
        train_years=years[:i]; val_years=years[i:i+validation_years]
        if not val_years: break
        train=frame.index[dates.dt.year.isin(train_years)]; val=frame.index[dates.dt.year.isin(val_years)]
        if len(train) and len(val):
            end=dates.loc[train].max(); start=dates.loc[val].min()
            if end>=start: raise ValueError("Temporal leakage: training overlaps validation")
            folds.append(Fold(train,val,end,start))
    return folds
def asof_publication_join(left:pd.DataFrame,right:pd.DataFrame,by:str="symbol",publication_column:str="publication_timestamp")->pd.DataFrame:
    l=left.sort_values("timestamp"); r=right.sort_values(publication_column)
    joined=pd.merge_asof(l,r,left_on="timestamp",right_on=publication_column,by=by,direction="backward")
    valid=joined[publication_column].dropna()<=joined.loc[joined[publication_column].notna(),"timestamp"]
    if not valid.all(): raise ValueError("Future information joined")
    return joined
