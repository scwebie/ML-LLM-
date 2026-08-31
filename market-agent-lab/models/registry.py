"""Filesystem metadata registry for reproducible paper models."""
import json
from pathlib import Path

from models.train import ModelBundle


class ModelRegistry:
    def __init__(self, root: str | Path = "data_store/models"):
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)
    def record(self, bundle: ModelBundle) -> Path:
        path = self.root / f"{bundle.model_version}.json"
        payload = {"model_version": bundle.model_version, "feature_version": bundle.feature_version, "feature_names": bundle.feature_names, "hyperparameters": bundle.hyperparameters, "training_period": bundle.training_period, "validation_period": bundle.validation_period, "metrics": bundle.metrics}
        path.write_text(json.dumps(payload, default=str, indent=2)); return path
