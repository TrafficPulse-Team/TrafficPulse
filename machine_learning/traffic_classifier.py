from pathlib import Path
import joblib
import numpy as np
from backend.schemas.traffic import IntelligenceResult
from .feature_engineering import FEATURE_COLUMNS, cv_result_to_features

class TrafficClassifier:
    def __init__(self, model_path="machine_learning/models/traffic_classifier.joblib"):
        self.model_path = Path(model_path)
        self.model = joblib.load(self.model_path) if self.model_path.exists() else None

    def predict(self, cv):
        f = cv_result_to_features(cv)
        if self.model is not None:
            X = [[f[c] for c in FEATURE_COLUMNS]]
            label = str(self.model.predict(X)[0])
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(X)[0]
                score = float(max(probs))
            else:
                score = 0.5
        else:
            # Honest fallback: deterministic baseline, not a trained ML claim.
            occupancy = f["road_occupancy"]
            flow = f["vehicle_flow"]
            score = min(1.0, 0.65*min(1.0, occupancy*4) + 0.35*min(1.0, flow/60))
            label = "LOW" if score < .25 else "MODERATE" if score < .5 else "HIGH" if score < .75 else "SEVERE"
        return IntelligenceResult(
            traffic_level=label,
            congestion_score=score,
            anomaly_detected=False,
            anomaly_type=None
        )
