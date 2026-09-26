"""Primary supervised behavioral detection model using Gradient Boosted Trees (XGBoost)."""
import logging
import joblib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger("TRACE.XGBoostDetector")

# Check if native xgboost is available
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    logger.info("Native xgboost package not installed; utilizing high-performance scikit-learn GradientBoosting.")

from sklearn.ensemble import GradientBoostingClassifier


class XGBoostDetector:
    """Primary supervised detector for classifying behavioral transaction patterns."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.is_fitted = False
        self.feature_names: List[str] = []
        self.model_backend = "xgboost" if XGB_AVAILABLE else "sklearn_gbm"

        if XGB_AVAILABLE:
            self.model = xgb.XGBClassifier(
                n_estimators=150,
                max_depth=4,
                learning_rate=0.08,
                subsample=0.85,
                colsample_bytree=0.85,
                random_state=random_state,
                eval_metric="logloss",
            )
        else:
            self.model = GradientBoostingClassifier(
                n_estimators=150,
                max_depth=4,
                learning_rate=0.08,
                subsample=0.85,
                random_state=random_state,
            )

    def train(self, X: pd.DataFrame, y: np.ndarray) -> Dict[str, float]:
        """Train model on behavioral feature matrix X and binary labels y."""
        self.feature_names = list(X.columns)
        X_vals = X.fillna(0.0).values
        self.model.fit(X_vals, y)
        self.is_fitted = True

        # Calculate training accuracy
        train_preds = self.model.predict(X_vals)
        acc = float(np.mean(train_preds == y))
        return {"training_accuracy": round(acc, 4), "backend": self.model_backend}

    def predict_probability(self, X: pd.DataFrame) -> np.ndarray:
        """
        Output: suspicious_probability (0.0 to 1.0).
        Strictly labeled as 'Model probability' (never proof).
        """
        if not self.is_fitted:
            # Baseline heuristic probability if not trained
            return np.zeros(len(X))

        # Reindex columns to guarantee consistency
        aligned_X = X.reindex(columns=self.feature_names, fill_value=0.0).fillna(0.0).values
        probs = self.model.predict_proba(aligned_X)[:, 1]
        return np.round(probs, 4)

    def get_feature_importances(self) -> Dict[str, float]:
        """Return relative feature importance scores."""
        if not self.is_fitted or not hasattr(self.model, "feature_importances_"):
            return {f: 0.0 for f in self.feature_names}

        importances = self.model.feature_importances_
        sorted_pairs = sorted(zip(self.feature_names, importances), key=lambda x: x[1], reverse=True)
        return {k: round(float(v), 5) for k, v in sorted_pairs}

    def save(self, filepath: Path):
        """Save model artifact locally."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "feature_names": self.feature_names,
                "is_fitted": self.is_fitted,
                "backend": self.model_backend,
            },
            filepath,
        )

    def load(self, filepath: Path):
        """Load model artifact from disk."""
        if filepath.exists():
            data = joblib.load(filepath)
            self.model = data["model"]
            self.feature_names = data["feature_names"]
            self.is_fitted = data["is_fitted"]
            self.model_backend = data.get("backend", "unknown")
