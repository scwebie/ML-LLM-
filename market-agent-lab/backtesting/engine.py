import pandas as pd

from backtesting.costs import CostModel
from backtesting.metrics import performance_metrics


def run_backtest(frame:pd.DataFrame,signal_column:str="signal",costs:CostModel|None=None)->tuple[pd.DataFrame,dict[str,float]]:
    costs = costs or CostModel()
    df=frame.sort_values("timestamp").copy(); df["position"]=df[signal_column].clip(-1,1).shift(1).fillna(0); df["asset_return"]=df.close.pct_change().fillna(0); df["turnover"]=df.position.diff().abs().fillna(0); df["strategy_return"]=df.position*df.asset_return-df.turnover*(costs.spread_bps+costs.slippage_bps)/10000
    return df,performance_metrics(df.strategy_return,df.asset_return,df.turnover.sum(),df.position.abs().mean())
