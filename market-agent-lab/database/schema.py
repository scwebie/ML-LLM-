"""Immutable, strongly typed domain records."""
from datetime import date, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)

class MarketObservation(FrozenModel):
    symbol: str; timestamp: datetime; open: float; high: float; low: float; close: float
    adjusted_close: float; volume: int = Field(ge=0)

class FundamentalObservation(FrozenModel):
    symbol: str; publication_timestamp: datetime; reporting_period: date
    revenue: float; revenue_growth: float; eps: float; eps_growth: float
    gross_margin: float; operating_margin: float; free_cash_flow: float; fcf_margin: float
    roic: float; debt: float; cash: float; pe_ratio: float | None = None
    price_to_sales: float | None = None

class MacroObservation(FrozenModel):
    timestamp: datetime; series_name: str; value: float; publication_timestamp: datetime
    vintage_timestamp: datetime | None = None

class AgentReport(FrozenModel):
    agent: str; agent_version: str; symbol: str; timestamp: datetime
    structured_features: dict[str, Any]; confidence: float = Field(ge=0, le=1)
    evidence_references: list[str]; reasoning_summary: str | None = None

class ModelPrediction(FrozenModel):
    prediction_id: UUID = Field(default_factory=uuid4); model_version: str; timestamp: datetime
    symbol: str; predicted_5d_excess_return: float; predicted_20d_excess_return: float
    probability_positive_5d: float = Field(ge=0, le=1)
    probability_positive_20d: float = Field(ge=0, le=1)
    predicted_volatility: float = Field(ge=0); confidence: float = Field(ge=0, le=1)
    feature_version: str

class Outcome(FrozenModel):
    prediction_id: UUID; realised_5d_excess_return: float; realised_20d_excess_return: float
    realised_volatility: float; completion_timestamp: datetime

class Side(StrEnum): BUY="BUY"; SELL="SELL"
class OrderType(StrEnum): MARKET="MARKET"; LIMIT="LIMIT"
class ApprovalStatus(StrEnum): PENDING="PENDING"; APPROVED="APPROVED"; REJECTED="REJECTED"

class PaperOrder(BaseModel):
    id: UUID = Field(default_factory=uuid4); symbol: str; side: Side; quantity: float = Field(gt=0)
    order_type: OrderType; proposed_price: float = Field(gt=0); timestamp: datetime
    strategy_model_version: str; risk_approval_status: ApprovalStatus = ApprovalStatus.PENDING

class PaperFill(FrozenModel):
    order_id: UUID; fill_timestamp: datetime; fill_price: float = Field(gt=0)
    quantity: float = Field(gt=0); slippage: float; commission: float = Field(ge=0)
