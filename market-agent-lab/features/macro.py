import pandas as pd


def macro_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.sort_values("timestamp").copy(); out["macro_change"] = out.groupby("series_name").value.diff(); return out
