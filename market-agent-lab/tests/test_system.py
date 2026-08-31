from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from backtesting.walk_forward import asof_publication_join, expanding_window_splits
from data.synthetic import generate_synthetic_dataset
from database.schema import ApprovalStatus, ModelPrediction, OrderType, PaperOrder, Side
from execution.paper import PaperBroker
from features.historical import find_analogues
from features.technical import agent_disagreement, compute_technical_features
from learning.champion_challenger import ModelCandidate, compare
from learning.outcomes import label_outcome
from models.predict import predict
from models.train import add_targets, train_models
from portfolio.risk import ReasonCode, RiskEngine, RiskLimits, RiskState


def order(**kw):
    values=dict(symbol="SYNTH_A",side=Side.BUY,quantity=10,order_type=OrderType.MARKET,proposed_price=100,timestamp=datetime.now(UTC),strategy_model_version="test");values.update(kw);return PaperOrder(**values)
def test_synthetic_deterministic_and_features():
    a=generate_synthetic_dataset(1);b=generate_synthetic_dataset(1);pd.testing.assert_frame_equal(a["market"],b["market"]);f=compute_technical_features(a["market"]);assert {"rsi_14","sma_200","atr_14","distance_52w_high"}<=set(f);assert f.groupby("symbol").return_1d.nth(0).isna().all()
def test_known_sma_return_and_disagreement():
    dates=pd.date_range("2020-01-01",periods=252);close=np.arange(1,253,dtype=float);df=pd.DataFrame({"symbol":"X","timestamp":dates,"close":close,"high":close+1,"low":close-1,"volume":np.arange(100,352)});out=compute_technical_features(df);assert out.iloc[9].sma_10==pytest.approx(5.5);assert out.iloc[5].return_5d==pytest.approx(5.0);assert agent_disagreement([1,-1])==1
def test_temporal_join_prevents_future_data():
    left=pd.DataFrame({"symbol":["X","X"],"timestamp":pd.to_datetime(["2021-01-02","2021-01-05"])});right=pd.DataFrame({"symbol":["X"],"publication_timestamp":pd.to_datetime(["2021-01-03"]),"value":[7]});joined=asof_publication_join(left,right);assert pd.isna(joined.iloc[0].value) and joined.iloc[1].value==7
def test_walk_forward_is_expanding_and_separated():
    df=pd.DataFrame({"timestamp":pd.date_range("2018-01-01","2023-12-31",freq="30D")});folds=expanding_window_splits(df,3);assert folds and all(f.train_end<f.validation_start for f in folds);assert len(folds[1].train_index)>len(folds[0].train_index)
def test_historical_similarity():
    h=pd.DataFrame({"x":[0,1,10],"future_5d_return":[.1,.2,-.5],"future_20d_return":[.2,.3,-.7]});r=find_analogues(h,{"x":0},["x"],k=1);assert r.number_of_analogues==1 and r.average_5d_return==.1
def test_lightgbm_training_and_prediction():
    data=compute_technical_features(generate_synthetic_dataset(2)["market"]);data=add_targets(data).dropna();features=["return_5d","rsi_14","realised_volatility_20d"];cut=data.timestamp.quantile(.75);train=data[data.timestamp<cut];val=data[data.timestamp>=cut];bundle=train_models(train,val,features);p=predict(bundle,val.head(2));assert len(p)==2 and 0<=p[0].probability_positive_5d<=1
def test_risk_limits_kill_duplicate_and_stale():
    state=RiskState(100_000);now=datetime.now(UTC);assert RiskEngine(RiskLimits(kill_switch=True)).evaluate(order(),state,now).reason==ReasonCode.KILL_SWITCH
    engine=RiskEngine();o=order();assert engine.evaluate(o,state,now).approved;assert engine.evaluate(o,state,now).reason==ReasonCode.DUPLICATE_ORDER
    assert RiskEngine().evaluate(order(),state,now-timedelta(days=4)).reason==ReasonCode.STALE_DATA
    assert RiskEngine().evaluate(order(quantity=1000),state,now).reason==ReasonCode.RISK_POSITION_LIMIT
def test_paper_fill_and_accounting():
    broker=PaperBroker(partial_fill_ratio=.5);o=order();o.risk_approval_status=ApprovalStatus.APPROVED;fill=broker.execute(o,100,datetime.now(UTC));assert fill and fill.quantity==5;assert broker.account.positions["SYNTH_A"].quantity==5;assert broker.account.cash<100_000;assert broker.execute(order(),100,datetime.now(UTC)) is None
def test_outcome_waits_for_horizon():
    p=ModelPrediction(model_version="v",timestamp=datetime.now(UTC),symbol="X",predicted_5d_excess_return=0,predicted_20d_excess_return=0,probability_positive_5d=.5,probability_positive_20d=.5,predicted_volatility=.2,confidence=.5,feature_version="v")
    with pytest.raises(ValueError):label_outcome(p,pd.Series([1]*5),pd.Series([1]*5),datetime.now(UTC))
    out=label_outcome(p,pd.Series(np.arange(100,121)),pd.Series([100]*21),datetime.now(UTC));assert out.realised_20d_excess_return==pytest.approx(.2)
def test_challenger_requires_multimetric_improvement():
    champion=ModelCandidate("c",1,-.1,.2,.1,.05,1);bad=ModelCandidate("x",2,-.4,.3,.09,.04,1);assert not compare(champion,bad).promoted
    good=ModelCandidate("x",1.1,-.1,.3,.09,.04,1);assert compare(champion,good).promoted
