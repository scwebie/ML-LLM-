# Model design

The v0.1 feature version contains lagged returns, trend distances, RSI, MACD, ATR, realised
volatility, volume surprise, macro state, and agent-score disagreement. Labels are forward 5- and
20-session stock returns less an abstract benchmark return. Regression estimates excess returns;
classification estimates the probability that each excess return is positive.

All observations are keyed by event time. Fundamentals and macro data join with backward-looking
`merge_asof` on their public publication timestamp—never reporting period. Forward labels are only
created after features are complete and their final 20 rows are discarded. The primary evaluation
uses configurable expanding chronological windows; random splitting is prohibited.

Retraining is controlled: completed predictions receive outcomes, drift can trigger challenger
training, and the challenger is evaluated on unseen walk-forward folds including transaction costs.
Promotion requires Sharpe improvement plus acceptable drawdown, information ratio, prediction
error, calibration, and turnover. Every decision records both versions and failed criteria. Raw
return alone can never promote a model.
