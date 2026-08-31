import pandas as pd

from database.schema import ModelPrediction, Outcome


def label_outcome(prediction:ModelPrediction,prices:pd.Series,benchmark:pd.Series,completion_timestamp)->Outcome:
    if len(prices)<21 or len(benchmark)<21:raise ValueError("Target horizon has not completed")
    excess=lambda n: prices.iloc[n]/prices.iloc[0]-1-(benchmark.iloc[n]/benchmark.iloc[0]-1)
    return Outcome(prediction_id=prediction.prediction_id,realised_5d_excess_return=excess(5),realised_20d_excess_return=excess(20),realised_volatility=prices.pct_change().iloc[1:21].std()*252**.5,completion_timestamp=completion_timestamp)
