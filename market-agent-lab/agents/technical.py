from pydantic import BaseModel, Field


class TechnicalAssessment(BaseModel):
    trend_score:float=Field(ge=-1,le=1);momentum_score:float=Field(ge=-1,le=1);volatility_risk:float=Field(ge=0,le=1);volume_confirmation:float=Field(ge=-1,le=1);technical_confidence:float=Field(ge=0,le=1)
def deterministic_fallback(features:dict[str,float])->TechnicalAssessment:
    clip=lambda x,a,b:max(a,min(b,x));return TechnicalAssessment(trend_score=clip(features.get("distance_sma_50",0)*10,-1,1),momentum_score=clip(features.get("return_20d",0)*5,-1,1),volatility_risk=clip(features.get("realised_volatility_20d",.2),0,1),volume_confirmation=clip(features.get("volume_zscore_20d",0)/3,-1,1),technical_confidence=.7)
