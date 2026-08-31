from datetime import UTC, datetime

import numpy as np
import pandas as pd

from database.schema import ModelPrediction
from models.train import ModelBundle


def predict(bundle:ModelBundle,frame:pd.DataFrame)->list[ModelPrediction]:
    x=frame[bundle.feature_names]; r5=bundle.models["target_5d"].predict(x); r20=bundle.models["target_20d"].predict(x); p5=bundle.models["positive_5d"].predict_proba(x)[:,1]; p20=bundle.models["positive_20d"].predict_proba(x)[:,1]
    vol=frame.get("realised_volatility_20d",pd.Series(.2,index=frame.index)).fillna(.2).to_numpy(); disagreement=frame.get("agent_disagreement",pd.Series(0,index=frame.index)).fillna(0).to_numpy()
    return [ModelPrediction(model_version=bundle.model_version,timestamp=pd.Timestamp(row.timestamp).to_pydatetime() if "timestamp" in frame else datetime.now(UTC),symbol=row.symbol,predicted_5d_excess_return=float(r5[i]),predicted_20d_excess_return=float(r20[i]),probability_positive_5d=float(p5[i]),probability_positive_20d=float(p20[i]),predicted_volatility=max(float(vol[i]),0),confidence=float(np.clip((abs(p5[i]-.5)+abs(p20[i]-.5))*(1-min(disagreement[i],1)),0,1)),feature_version=bundle.feature_version) for i,row in enumerate(frame.itertuples())]
