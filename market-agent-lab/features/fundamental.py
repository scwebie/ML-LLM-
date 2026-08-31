import pandas as pd


def fundamental_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy(); out["net_cash_to_revenue"] = (out.cash - out.debt) / out.revenue; out["earnings_quality"] = out.fcf_margin - out.operating_margin; return out
