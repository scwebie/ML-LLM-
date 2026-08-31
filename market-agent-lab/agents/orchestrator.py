"""Research-only orchestration. Agent outputs can only become features, never orders."""
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from agents.technical import deterministic_fallback
from features.technical import agent_disagreement


class ResearchOrchestrator:
    """Offline implementation of the same structured boundary used by hosted SDK agents."""
    def run_offline(self, symbol: str, features: dict[str, float]) -> dict[str, Any]:
        technical = deterministic_fallback(features)
        scores = [technical.trend_score, technical.momentum_score, technical.volume_confirmation]
        return {"symbol": symbol, "technical": technical.model_dump(), "agent_disagreement": agent_disagreement(scores)}
    @staticmethod
    def sdk_available() -> bool:
        try: version("openai-agents")
        except PackageNotFoundError: return False
        return True
