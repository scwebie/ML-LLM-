from learning.champion_challenger import ModelCandidate, PromotionDecision, compare


def evaluate_challenger(champion:ModelCandidate,challenger:ModelCandidate)->PromotionDecision:return compare(champion,challenger)
