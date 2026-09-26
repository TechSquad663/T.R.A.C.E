"""Feature preprocessing and robust scaling."""
import logging
import joblib
from pathlib import Path
from typing import Tuple, List, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler

logger = logging.getLogger("TRACE.Preprocessor")


class DataPreprocessor:
    """Preprocesses and normalizes feature vectors using RobustScaler to handle heavy-tailed financial distributions."""

    def __init__(self):
        self.scaler = RobustScaler()
        self.feature_names: List[str] = []
        self.is_fitted = False

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """Fit scaler on feature DataFrame and transform."""
        self.feature_names = list(X.columns)
        X_clean = X.fillna(0.0).values
        X_scaled = self.scaler.fit_transform(X_clean)
        self.is_fitted = True
        return X_scaled

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform features using fitted scaler."""
        if not self.is_fitted:
            return X.fillna(0.0).values
        # Align columns
        aligned_df = X.reindex(columns=self.feature_names, fill_value=0.0)
        return self.scaler.transform(aligned_df.fillna(0.0).values)

    def save(self, filepath: Path):
        """Save scaler artifact."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"scaler": self.scaler, "feature_names": self.feature_names, "is_fitted": self.is_fitted}, filepath)

    def load(self, filepath: Path):
        """Load scaler artifact."""
        if filepath.exists():
            data = joblib.load(filepath)
            self.scaler = data["scaler"]
            self.feature_names = data["feature_names"]
            self.is_fitted = data["is_fitted"]
