"""Behavioral clustering engine using DBSCAN with 2D projection for forensic analysis."""
import logging
import joblib
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger("TRACE.Clustering")


class BehavioralClusterer:
    """Discovers behavioral cohorts using density-based spatial clustering (DBSCAN)."""

    def __init__(self, eps: float = 0.65, min_samples: int = 4):
        self.eps = eps
        self.min_samples = min_samples
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2, random_state=42)
        self.dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        self.is_fitted = False
        self.feature_names: List[str] = []

    def fit_predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, Dict[int, Dict[str, Any]]]:
        """
        Cluster entities by behavioral traits.
        Returns:
            cluster_labels: array of cluster IDs (-1 = noise)
            pca_coords: Nx2 array of 2D coordinates for visual mapping
            cluster_summaries: metadata about each cluster (size, signature traits)
        """
        self.feature_names = list(X.columns)
        X_vals = X.fillna(0.0).values

        if len(X_vals) == 0:
            return np.array([]), np.zeros((0, 2)), {}

        # Scale features
        X_scaled = self.scaler.fit_transform(X_vals)

        # Apply DBSCAN
        labels = self.dbscan.fit_predict(X_scaled)
        self.is_fitted = True

        # Compute 2D PCA projection for link/cluster view
        if len(X_vals) >= 2:
            pca_coords = self.pca.fit_transform(X_scaled)
        else:
            pca_coords = np.zeros((len(X_vals), 2))

        # Generate cluster profiles
        cluster_summaries: Dict[int, Dict[str, Any]] = {}
        unique_labels = set(labels)

        for cid in unique_labels:
            mask = (labels == cid)
            size = int(np.sum(mask))
            if cid == -1:
                desc = "Outliers / Disparate entities (Statistical deviation; not evidence of wrongdoing)"
            else:
                desc = f"Behavioral Cohort #{cid} ({size} entities sharing comparable flow characteristics)"

            # Top centroid traits
            sub_feats = X_vals[mask]
            centroid = np.mean(sub_feats, axis=0)
            top_indices = np.argsort(np.abs(centroid))[-4:][::-1]
            top_traits = [
                f"{self.feature_names[idx]}: {centroid[idx]:.2f}"
                for idx in top_indices if idx < len(self.feature_names)
            ]

            cluster_summaries[int(cid)] = {
                "cluster_id": int(cid),
                "size": size,
                "description": desc,
                "is_noise": bool(cid == -1),
                "characteristic_traits": top_traits,
            }

        return labels, np.round(pca_coords, 3), cluster_summaries

    def save(self, filepath: Path):
        """Save clustering artifact."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "scaler": self.scaler,
                "pca": self.pca,
                "feature_names": self.feature_names,
                "eps": self.eps,
                "min_samples": self.min_samples,
                "is_fitted": self.is_fitted,
            },
            filepath,
        )

    def load(self, filepath: Path):
        """Load clustering artifact."""
        if filepath.exists():
            data = joblib.load(filepath)
            self.scaler = data["scaler"]
            self.pca = data["pca"]
            self.feature_names = data["feature_names"]
            self.eps = data.get("eps", 0.65)
            self.min_samples = data.get("min_samples", 4)
            self.is_fitted = data.get("is_fitted", False)
