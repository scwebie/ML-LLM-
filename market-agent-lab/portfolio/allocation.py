from database.schema import ModelPrediction


def allocate(predictions:list[ModelPrediction],max_weight:float=.1)->dict[str,float]:
    raw={p.symbol:(p.predicted_5d_excess_return*p.probability_positive_5d/max(p.predicted_volatility,.05)) for p in predictions}; scale=sum(abs(v) for v in raw.values()) or 1
    return {s:max(-max_weight,min(max_weight,v/scale)) for s,v in raw.items()}
