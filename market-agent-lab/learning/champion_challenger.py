from dataclasses import dataclass


@dataclass(frozen=True)
class ModelCandidate: version:str; sharpe:float; max_drawdown:float; information_ratio:float; prediction_error:float; calibration_error:float; turnover:float
@dataclass(frozen=True)
class PromotionCriteria: min_sharpe_improvement:float=.05; max_drawdown_deterioration:float=.02; min_information_ratio:float=0; max_error_deterioration:float=0; max_calibration_deterioration:float=.02; max_turnover_multiple:float=1.25
@dataclass(frozen=True)
class PromotionDecision: champion_version:str; challenger_version:str; promoted:bool; reasons:tuple[str,...]
def compare(champion:ModelCandidate,challenger:ModelCandidate,c:PromotionCriteria|None=None)->PromotionDecision:
    c = c or PromotionCriteria()
    checks={"sharpe":challenger.sharpe>=champion.sharpe+c.min_sharpe_improvement,"drawdown":challenger.max_drawdown>=champion.max_drawdown-c.max_drawdown_deterioration,"information_ratio":challenger.information_ratio>=c.min_information_ratio,"prediction_error":challenger.prediction_error<=champion.prediction_error+c.max_error_deterioration,"calibration":challenger.calibration_error<=champion.calibration_error+c.max_calibration_deterioration,"turnover":challenger.turnover<=champion.turnover*c.max_turnover_multiple}
    return PromotionDecision(champion.version,challenger.version,all(checks.values()),tuple(k for k,v in checks.items() if not v))
ChampionModel=ModelCandidate; ChallengerModel=ModelCandidate
