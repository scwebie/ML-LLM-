from pydantic import BaseModel, Field


class EventAssessment(BaseModel):
    event_sentiment:float=Field(ge=-1,le=1);event_uncertainty:float=Field(ge=0,le=1);earnings_event_score:float=Field(ge=-1,le=1);macro_event_score:float=Field(ge=-1,le=1);news_sentiment:float=Field(ge=-1,le=1);expected_catalyst_direction:float=Field(ge=-1,le=1);confidence:float=Field(ge=0,le=1)
