"""Deterministic, explicitly fictional market data with weak regime relationships."""
from pathlib import Path

import numpy as np
import pandas as pd

SYMBOLS = ("SYNTH_A", "SYNTH_B", "SYNTH_C", "SYNTH_D")
def generate_synthetic_dataset(years: int = 6, seed: int = 42) -> dict[str, pd.DataFrame]:
    rng=np.random.default_rng(seed); dates=pd.bdate_range("2018-01-01", periods=252*years)
    regime=np.resize(np.repeat([0,1,2],126),len(dates)); macro_signal=np.sin(np.arange(len(dates))/80)
    rows=[]
    for j,symbol in enumerate(SYMBOLS):
        noise=rng.normal(0,0.011+j*.001,len(dates)); drift=np.choose(regime,[.0004,-.0003,.0001])
        returns=drift+.0008*macro_signal+noise; close=(70+10*j)*np.exp(np.cumsum(returns))
        open_=close*np.exp(rng.normal(0,.002,len(dates))); spread=np.abs(rng.normal(.006,.002,len(dates)))
        volume=rng.lognormal(13+j*.1,.25,len(dates)).astype(int)
        rows.extend(zip([symbol]*len(dates),dates,open_,np.maximum(open_,close)*(1+spread),np.minimum(open_,close)*(1-spread),close,close,volume,regime,macro_signal,strict=True))
    market=pd.DataFrame(rows,columns="symbol timestamp open high low close adjusted_close volume regime macro_signal".split())
    fundamentals=[]
    for symbol in SYMBOLS:
        for d in pd.date_range(dates.min(),dates.max(),freq="QE"):
            base=1e9*(1+.04*SYMBOLS.index(symbol)); growth=.05+.02*np.sin(d.dayofyear/365*6.28)+rng.normal(0,.015)
            fundamentals.append((symbol,d+pd.Timedelta(days=35),d.date(),base,growth,2+growth, growth/2,.42,.18,base*.12,.12,.11,base*.2,base*.1,18-growth*20))
    fundamentals=pd.DataFrame(fundamentals,columns="symbol publication_timestamp reporting_period revenue revenue_growth eps eps_growth gross_margin operating_margin free_cash_flow fcf_margin roic debt cash pe_ratio".split())
    macro=pd.DataFrame({"timestamp":dates,"series_name":"SYNTH_GROWTH","value":macro_signal,"publication_timestamp":dates+pd.Timedelta(days=1),"vintage_timestamp":dates+pd.Timedelta(days=1)})
    news=market[["symbol","timestamp"]].copy(); news["sentiment"]=np.clip(.15*market["macro_signal"]+rng.normal(0,.5,len(market)),-1,1); news["is_synthetic"]=True
    return {"market":market,"fundamentals":fundamentals,"macro":macro,"news":news}

def write_synthetic_dataset(path: str|Path="data_store", years: int=6) -> dict[str,pd.DataFrame]:
    path=Path(path); path.mkdir(parents=True,exist_ok=True); data=generate_synthetic_dataset(years)
    for name,frame in data.items(): frame.to_parquet(path/f"synthetic_{name}.parquet",index=False)
    return data
