from dataclasses import dataclass


@dataclass(frozen=True)
class CostModel:
    commission_per_order:float=1.0; spread_bps:float=4; slippage_bps:float=3
    def cost(self,notional:float)->float: return self.commission_per_order+abs(notional)*(self.spread_bps+self.slippage_bps)/10000
