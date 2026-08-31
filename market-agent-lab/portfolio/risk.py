from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

from database.schema import PaperOrder


class ReasonCode(StrEnum):
    APPROVED="APPROVED"; RISK_POSITION_LIMIT="RISK_POSITION_LIMIT"; RISK_GROSS_EXPOSURE="RISK_GROSS_EXPOSURE"; RISK_NET_EXPOSURE="RISK_NET_EXPOSURE"; RISK_SECTOR_CONCENTRATION="RISK_SECTOR_CONCENTRATION"; RISK_PORTFOLIO_VOLATILITY="RISK_PORTFOLIO_VOLATILITY"; RISK_DAILY_LOSS="RISK_DAILY_LOSS"; RISK_DRAWDOWN="RISK_DRAWDOWN"; STALE_DATA="STALE_DATA"; DUPLICATE_ORDER="DUPLICATE_ORDER"; INVALID_PRICE="INVALID_PRICE"; KILL_SWITCH="KILL_SWITCH"
@dataclass(frozen=True)
class RiskLimits:
    max_position_weight:float=.15; max_gross_exposure:float=1.; max_net_exposure:float=.5; max_sector_concentration:float=.3; max_portfolio_volatility:float=.3; max_daily_loss:float=.03; max_drawdown:float=.2; stale_after:timedelta=timedelta(days=3); kill_switch:bool=False
@dataclass(frozen=True)
class RiskState:
    equity:float; gross_exposure:float=0; net_exposure:float=0; portfolio_volatility:float=0; daily_pnl:float=0; drawdown:float=0
@dataclass(frozen=True)
class RiskDecision: approved:bool; reason:ReasonCode
class RiskEngine:
    def __init__(self,limits:RiskLimits|None=None): self.limits=limits or RiskLimits(); self._seen:set[str]=set()
    def evaluate(self,order:PaperOrder,state:RiskState,market_timestamp:datetime)->RiskDecision:
        l=self.limits; notional=order.quantity*order.proposed_price; signed=notional*(1 if order.side.value=="BUY" else -1); weight=notional/state.equity if state.equity else float("inf")
        checks=[(l.kill_switch,ReasonCode.KILL_SWITCH),(str(order.id) in self._seen,ReasonCode.DUPLICATE_ORDER),(order.proposed_price<=0,ReasonCode.INVALID_PRICE),(order.timestamp-market_timestamp>l.stale_after,ReasonCode.STALE_DATA),(state.drawdown<=-l.max_drawdown,ReasonCode.RISK_DRAWDOWN),(state.daily_pnl/state.equity<=-l.max_daily_loss,ReasonCode.RISK_DAILY_LOSS),(state.portfolio_volatility>l.max_portfolio_volatility,ReasonCode.RISK_PORTFOLIO_VOLATILITY),(weight>l.max_position_weight,ReasonCode.RISK_POSITION_LIMIT),(state.gross_exposure+weight>l.max_gross_exposure,ReasonCode.RISK_GROSS_EXPOSURE),(abs(state.net_exposure+signed/state.equity)>l.max_net_exposure,ReasonCode.RISK_NET_EXPOSURE)]
        self._seen.add(str(order.id))
        for condition,reason in checks:
            if condition:return RiskDecision(False,reason)
        return RiskDecision(True,ReasonCode.APPROVED)
