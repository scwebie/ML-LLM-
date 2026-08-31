from pydantic import BaseModel, Field


class FundamentalAssessment(BaseModel):
    """All component scores range [-1,1], confidence [0,1]."""
    growth_score:float=Field(ge=-1,le=1);profitability_score:float=Field(ge=-1,le=1);balance_sheet_score:float=Field(ge=-1,le=1);valuation_score:float=Field(ge=-1,le=1);earnings_quality_score:float=Field(ge=-1,le=1);guidance_score:float=Field(ge=-1,le=1);fundamental_confidence:float=Field(ge=0,le=1)
