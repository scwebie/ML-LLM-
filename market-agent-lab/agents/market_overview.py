from typing import Literal

from pydantic import BaseModel, Field


class MarketOverviewAssessment(BaseModel):
    risk_appetite_score:float=Field(ge=-1,le=1);liquidity_score:float=Field(ge=-1,le=1);volatility_regime:Literal["low","normal","high"];growth_regime:Literal["contracting","stable","expanding"];inflation_regime:Literal["falling","stable","rising"];monetary_policy_regime:Literal["easing","neutral","tightening"];market_breadth_score:float=Field(ge=-1,le=1);overall_macro_confidence:float=Field(ge=0,le=1)
