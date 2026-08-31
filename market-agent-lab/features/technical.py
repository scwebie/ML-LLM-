"""Deterministic technical feature calculations; no LLM participates."""
import numpy as np
import pandas as pd


def compute_technical_features(frame: pd.DataFrame) -> pd.DataFrame:
    required={"symbol","timestamp","high","low","close","volume"}
    if missing:=required-set(frame.columns): raise ValueError(f"Missing columns: {sorted(missing)}")
    df=frame.sort_values(["symbol","timestamp"]).copy(); parts=[]
    for _,g in df.groupby("symbol",sort=False):
        g=g.copy(); c=g.close.astype(float); ret=c.pct_change()
        for n in (1,5,10,20,60): g[f"return_{n}d"]=c.pct_change(n)
        for n in (10,20,50,100,200): g[f"sma_{n}"]=c.rolling(n).mean()
        for n in (20,50,200): g[f"distance_sma_{n}"]=c/g[f"sma_{n}"]-1
        delta=c.diff(); gain=delta.clip(lower=0).rolling(14).mean(); loss=(-delta.clip(upper=0)).rolling(14).mean()
        g["rsi_14"]=100-(100/(1+gain/loss.replace(0,np.nan)))
        macd=c.ewm(span=12,adjust=False).mean()-c.ewm(span=26,adjust=False).mean(); g["macd"]=macd; g["macd_signal"]=macd.ewm(span=9,adjust=False).mean()
        prev=c.shift(); tr=pd.concat([(g.high-g.low),(g.high-prev).abs(),(g.low-prev).abs()],axis=1).max(axis=1); g["atr_14"]=tr.rolling(14).mean()
        mean=c.rolling(20).mean(); std=c.rolling(20).std(); g["bollinger_position"]=(c-(mean-2*std))/(4*std)
        for n in (10,20,60): g[f"realised_volatility_{n}d"]=ret.rolling(n).std()*np.sqrt(252)
        vm=g.volume.rolling(20).mean(); vs=g.volume.rolling(20).std(); g["volume_zscore_20d"]=(g.volume-vm)/vs; g["relative_volume"]=g.volume/vm
        hi=g.high.rolling(252).max(); lo=g.low.rolling(252).min(); g["distance_52w_high"]=c/hi-1; g["distance_52w_low"]=c/lo-1
        parts.append(g)
    return pd.concat(parts).sort_index()

def agent_disagreement(scores: list[float]) -> float:
    return float(np.std(scores,ddof=0)) if scores else 0.0
