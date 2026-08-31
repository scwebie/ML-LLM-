import numpy as np
import pandas as pd
from pydantic import BaseModel, Field


class HistoricalAnalogueResult(BaseModel):
    number_of_analogues:int; average_5d_return:float; median_5d_return:float
    probability_positive_5d:float; average_20d_return:float; median_20d_return:float
    probability_positive_20d:float; percentile_10_return:float; percentile_90_return:float
    similarity_confidence:float=Field(ge=0,le=1)
def find_analogues(history:pd.DataFrame,current:dict[str,float],feature_names:list[str],k:int=20,weights:np.ndarray|None=None)->HistoricalAnalogueResult:
    clean=history.dropna(subset=feature_names+["future_5d_return","future_20d_return"]); x=clean[feature_names].to_numpy(float); mu=x.mean(0); sigma=x.std(0); sigma[sigma==0]=1
    current_x=np.array([current[n] for n in feature_names]); w=np.ones(len(feature_names)) if weights is None else weights
    distance=np.sqrt(np.sum(w*((x-mu)/sigma-(current_x-mu)/sigma)**2,axis=1)); chosen=clean.iloc[np.argsort(distance)[:min(k,len(clean))]]; d=np.sort(distance)[:len(chosen)]; r5=chosen.future_5d_return; r20=chosen.future_20d_return
    return HistoricalAnalogueResult(number_of_analogues=len(chosen),average_5d_return=r5.mean(),median_5d_return=r5.median(),probability_positive_5d=(r5>0).mean(),average_20d_return=r20.mean(),median_20d_return=r20.median(),probability_positive_20d=(r20>0).mean(),percentile_10_return=np.percentile(r20,10),percentile_90_return=np.percentile(r20,90),similarity_confidence=float(1/(1+d.mean())))
