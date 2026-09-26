"""Secondary unsupervised anomaly detector using Isolation Forest."""
import logging
import joblib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

logger = logging.getLogger("TRACE.IsolationForest")


class IsolationForestDetector:
    """Unsupervised anomaly detector measuring multivariate deviation from population baseline."""

    def __init__(self, contamination: float = 0.08, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=120,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self.is_fitted = False
        self.feature_names: List[str] = []

    def fit(self, X: pd.DataFrame):
        """Fit Isolation Forest on population feature matrix."""
        self.feature_names = list(X.columns)
        X_vals = X.fillna(0.0).values
        self.model.fit(X_vals)
        self.is_fitted = True

    def predict_anomaly_scores(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Output:
            anomaly_scores: 0.0 (normal) to 1.0 (highly anomalous)
            is_anomaly: boolean array indicating whether point is in contamination tail
        """
        if not self.is_fitted:
            self.fit(X)

        aligned_X = X.reindex(columns=self.feature_names, fill_value=0.0).fillna(0.0).values
        # raw decision_function: lower means more anomalous
        raw_scores = self.model.decision_function(aligned_X)
        # Normalize into 0 to 1 range (inverted so higher = more anomalous)
        min_s, max_s = raw_scores.min(), raw_scores.max()
        if max_s > min_s:
            norm_scores = 1.0 - ((raw_scores - min_s) / (max_s - min_s))
        else:
            norm_scores = np.zeros_like(raw_scores)

        # -1 = anomaly, 1 = normal in sklearn IsolationForest
        preds = self.model.predict(aligned_X)
        is_anomaly = preds == -1

        return np.round(norm_scores, 4), is_anomaly

    def save(self, filepath: Path):
        """Save Isolation Forest model artifact."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "feature_names": self.feature_names,
                "is_fitted": self.is_fitted,
                "contamination": self.contamination,
            },
            filepath,
        )

    def load(self, filepath: Path):
        """Load Isolation Forest artifact."""
        if filepath.exists():
            data = joblib.load(filepath)
            self.model = data["model"]
            self.feature_names = data["feature_names"]
            self.is_fitted = data["is_fitted"]
            self.contamination = data.get("contamination", 0.08)
