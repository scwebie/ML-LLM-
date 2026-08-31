import argparse
import json
from pathlib import Path

import numpy as np

from agents.orchestrator import ResearchOrchestrator
from backtesting.engine import run_backtest
from backtesting.walk_forward import expanding_window_splits
from data.synthetic import write_synthetic_dataset
from database.schema import ApprovalStatus, OrderType, PaperOrder, Side
from execution.paper import PaperBroker
from features.feature_store import FeatureStore
from features.technical import compute_technical_features
from models.predict import predict
from models.train import add_targets, train_models
from portfolio.allocation import allocate
from portfolio.risk import RiskEngine, RiskState

FEATURES=["return_5d","return_20d","distance_sma_20","distance_sma_50","rsi_14","macd","atr_14","realised_volatility_20d","volume_zscore_20d","macro_signal"]
def demo()->dict:
    data=write_synthetic_dataset(); featured=compute_technical_features(data["market"]); labelled=add_targets(featured).dropna(subset=FEATURES+["target_5d","target_20d"]);FeatureStore().write(labelled,"technical-v1")
    folds=expanding_window_splits(labelled,min_train_years=3); fold=folds[-1]; train=labelled.loc[fold.train_index];valid=labelled.loc[fold.validation_index];bundle=train_models(train,valid,FEATURES)
    latest=valid.sort_values("timestamp").groupby("symbol").tail(1);predictions=predict(bundle,latest);weights=allocate(predictions);broker=PaperBroker();risk=RiskEngine();risk_rows=[];fills=[]
    for p in predictions:
        row=latest[latest.symbol==p.symbol].iloc[0];qty=abs(weights[p.symbol])*broker.account.equity/row.close
        market_time = row.timestamp.to_pydatetime()
        order=PaperOrder(symbol=p.symbol,side=Side.BUY if weights[p.symbol]>=0 else Side.SELL,quantity=max(qty,.001),order_type=OrderType.MARKET,proposed_price=row.close,timestamp=market_time,strategy_model_version=bundle.model_version)
        decision=risk.evaluate(order,RiskState(equity=broker.account.equity),market_time);risk_rows.append({"order_id":str(order.id),"status":"APPROVED" if decision.approved else "REJECTED","reason":decision.reason})
        if decision.approved:order.risk_approval_status=ApprovalStatus.APPROVED;fill=broker.execute(order,row.close,market_time);fills.append(fill.model_dump(mode="json") if fill else None)
    bt=valid[valid.symbol==valid.symbol.iloc[0]].copy()
    bt_predictions=predict(bundle,bt)
    bt["signal"]=[np.sign(p.predicted_5d_excess_return) for p in bt_predictions]
    _,metrics=run_backtest(bt)
    report=ResearchOrchestrator().run_offline(latest.iloc[0].symbol,latest.iloc[0][FEATURES].to_dict());importance=dict(zip(FEATURES,bundle.models["target_5d"].feature_importances_.astype(int),strict=True))
    summary={"mode":"PAPER_SIMULATION_ONLY","model_version":bundle.model_version,"model_metrics":bundle.metrics,"feature_importance":importance,"backtest_metrics":metrics,"example_prediction":predictions[0].model_dump(mode="json"),"risk_decisions":risk_rows,"example_fill":next((f for f in fills if f),None),"cash":broker.account.cash,"equity":broker.account.equity,"positions":{s:p.quantity for s,p in broker.account.positions.items()},"agent_report":report,"agent_disagreement":report["agent_disagreement"],"kill_switch":False}
    Path("data_store/demo_summary.json").write_text(json.dumps(summary,indent=2,default=str));print(json.dumps(summary,indent=2,default=str));return summary
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=["demo"]);args=parser.parse_args();demo()
