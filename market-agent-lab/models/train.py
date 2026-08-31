"""LightGBM multi-target alpha training without random temporal splits."""
from dataclasses import dataclass
from datetime import date

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, roc_auc_score

TARGETS=("target_5d","target_20d","positive_5d","positive_20d")
@dataclass
class ModelBundle:
    models:dict[str,object]; feature_names:list[str]; model_version:str; feature_version:str
    training_period:tuple[date,date]; validation_period:tuple[date,date]; hyperparameters:dict; metrics:dict[str,float]
def add_targets(frame:pd.DataFrame,benchmark:pd.Series|None=None)->pd.DataFrame:
    out=frame.sort_values(["symbol","timestamp"]).copy(); grouped=out.groupby("symbol").close
    for n in (5,20): out[f"target_{n}d"]=grouped.shift(-n)/out.close-1
    if benchmark is not None:
        bench=benchmark.reindex(out.timestamp).to_numpy();
        for n in (5,20): out[f"target_{n}d"]-=pd.Series(bench).shift(-n).to_numpy()/bench-1
    out["positive_5d"]=(out.target_5d>0).astype(int); out["positive_20d"]=(out.target_20d>0).astype(int); return out

def train_models(train:pd.DataFrame,validation:pd.DataFrame,features:list[str],model_version:str="lgbm-v0.1",feature_version:str="technical-v1")->ModelBundle:
    params={"n_estimators":60,"learning_rate":.05,"max_depth":4,"num_leaves":15,"random_state":42,"verbosity":-1,"n_jobs":1}
    models={}; metrics={}; mapping={"target_5d":"target_5d","target_20d":"target_20d","positive_5d":"positive_5d","positive_20d":"positive_20d"}
    for name,target in mapping.items():
        cls=name.startswith("positive"); model=(lgb.LGBMClassifier if cls else lgb.LGBMRegressor)(**params); model.fit(train[features],train[target]); models[name]=model
        pred=model.predict_proba(validation[features])[:,1] if cls else model.predict(validation[features]); metrics[("auc_" if cls else "rmse_")+name]=float(roc_auc_score(validation[target],pred) if cls and validation[target].nunique()>1 else np.sqrt(mean_squared_error(validation[target],pred)))
    return ModelBundle(models,features,model_version,feature_version,(train.timestamp.min().date(),train.timestamp.max().date()),(validation.timestamp.min().date(),validation.timestamp.max().date()),params,metrics)
