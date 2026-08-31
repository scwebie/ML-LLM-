import numpy as np
import pandas as pd


def performance_metrics(returns:pd.Series,benchmark:pd.Series|None=None,turnover:float=0,exposure:float=0)->dict[str,float]:
    r=returns.fillna(0); equity=(1+r).cumprod(); years=max(len(r)/252,1/252); total=equity.iloc[-1]-1; vol=r.std()*np.sqrt(252); downside=r[r<0].std()*np.sqrt(252); dd=equity/equity.cummax()-1; wins=r[r>0]; losses=r[r<0]
    result={"total_return":total,"cagr":equity.iloc[-1]**(1/years)-1,"annualised_volatility":vol,"sharpe":r.mean()*252/vol if vol else 0,"sortino":r.mean()*252/downside if downside else 0,"maximum_drawdown":dd.min(),"calmar":(equity.iloc[-1]**(1/years)-1)/abs(dd.min()) if dd.min() else 0,"hit_rate":(r>0).mean(),"profit_factor":wins.sum()/abs(losses.sum()) if losses.sum() else 0,"turnover":turnover,"average_win":wins.mean() if len(wins) else 0,"average_loss":losses.mean() if len(losses) else 0,"exposure":exposure,"average_holding_period":1.0}
    if benchmark is not None:
        b=benchmark.reindex(r.index).fillna(0); cov=np.cov(r,b); beta=cov[0,1]/cov[1,1] if cov[1,1] else 0; active=r-b; result.update(beta=beta,alpha=(r.mean()-beta*b.mean())*252,information_ratio=active.mean()/active.std()*np.sqrt(252) if active.std() else 0)
    else: result.update(beta=0,alpha=0,information_ratio=0)
    return {k:float(v) for k,v in result.items()}
