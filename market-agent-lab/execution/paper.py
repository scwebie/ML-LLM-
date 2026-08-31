"""Internal simulation broker. There are deliberately no external broker adapters."""
from dataclasses import dataclass, field
from datetime import datetime

from database.schema import ApprovalStatus, OrderType, PaperFill, PaperOrder, Side


@dataclass
class Position: quantity:float=0; average_price:float=0
@dataclass
class AccountState:
    cash:float; equity:float; realised_pnl:float=0; unrealised_pnl:float=0; positions:dict[str,Position]=field(default_factory=dict)
    @property
    def available_buying_power(self)->float:return max(self.cash,0)
class PaperBroker:
    def __init__(self,initial_cash:float=100_000,commission:float=1,slippage_bps:float=3,partial_fill_ratio:float=1): self.account=AccountState(initial_cash,initial_cash); self.commission=commission; self.slippage_bps=slippage_bps; self.partial_fill_ratio=partial_fill_ratio
    def execute(self,order:PaperOrder,market_price:float,timestamp:datetime)->PaperFill|None:
        if order.risk_approval_status!=ApprovalStatus.APPROVED:return None
        if order.order_type==OrderType.LIMIT and ((order.side==Side.BUY and market_price>order.proposed_price) or (order.side==Side.SELL and market_price<order.proposed_price)):return None
        qty=order.quantity*self.partial_fill_ratio; direction=1 if order.side==Side.BUY else -1; slippage=market_price*self.slippage_bps/10000*direction; price=market_price+slippage; cost=qty*price*direction+self.commission
        if direction>0 and cost>self.account.cash:return None
        pos=self.account.positions.setdefault(order.symbol,Position()); old=pos.quantity
        if direction>0: pos.average_price=(old*pos.average_price+qty*price)/(old+qty); pos.quantity+=qty
        else:
            qty=min(qty,max(old,0)); self.account.realised_pnl+=(price-pos.average_price)*qty; pos.quantity-=qty
        self.account.cash-=qty*price*direction+self.commission; self.account.equity=self.account.cash+sum(p.quantity*(price if s==order.symbol else p.average_price) for s,p in self.account.positions.items())
        return PaperFill(order_id=order.id,fill_timestamp=timestamp,fill_price=price,quantity=qty,slippage=slippage,commission=self.commission)
