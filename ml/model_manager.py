"""Central model manager for lifecycle orchestration, inference, and artifact storage."""
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from config.settings import get_settings
from .preprocessing import DataPreprocessor
from .xgboost_detector import XGBoostDetector
from .isolation_forest import IsolationForestDetector
from .clustering import BehavioralClusterer
from .explainability import ForensicExplainer
from .evaluation import ModelEvaluator

logger = logging.getLogger("TRACE.ModelManager")


class ModelManager:
    """Coordinates training, offline persistence, and multi-model behavioral inference."""

    def __init__(self, models_dir: Optional[Path] = None):
        self.settings = get_settings()
        self.models_dir = models_dir or self.settings.MODELS_DIR
        self.preprocessor = DataPreprocessor()
        self.supervised_detector = XGBoostDetector()
        self.isolation_forest = IsolationForestDetector()
        self.clusterer = BehavioralClusterer()
        self.explainer = ForensicExplainer(self.supervised_detector)
        self.evaluator = ModelEvaluator()
        self.is_ready = False

    def train_and_save_all(
        self,
        X_train: pd.DataFrame,
        y_train: np.ndarray,
    ) -> Dict[str, Any]:
        """Train all models offline and persist artifacts."""
        logger.info(f"Training models offline on {len(X_train)} samples...")
        
        # 1. Preprocessor
        self.preprocessor.fit_transform(X_train)
        self.preprocessor.save(self.models_dir / "preprocessor.joblib")

        # 2. Supervised Detector
        sup_metrics = self.supervised_detector.train(X_train, y_train)
        self.supervised_detector.save(self.models_dir / "xgboost_model.joblib")

        # 3. Isolation Forest
        self.isolation_forest.fit(X_train)
        self.isolation_forest.save(self.models_dir / "isolation_forest.joblib")

        # 4. Behavioral Clustering
        labels, coords, summaries = self.clusterer.fit_predict(X_train)
        self.clusterer.save(self.models_dir / "clusterer.joblib")

        # Re-initialize explainer with fitted model
        self.explainer = ForensicExplainer(self.supervised_detector)
        self.is_ready = True

        return {
            "status": "SUCCESS",
            "supervised_metrics": sup_metrics,
            "sample_count": len(X_train),
            "cluster_count": len(summaries),
        }

    def load_artifacts(self) -> bool:
        """Load pre-trained model artifacts from disk if available."""
        try:
            p_file = self.models_dir / "preprocessor.joblib"
            x_file = self.models_dir / "xgboost_model.joblib"
            i_file = self.models_dir / "isolation_forest.joblib"
            c_file = self.models_dir / "clusterer.joblib"

            if p_file.exists() and x_file.exists() and i_file.exists() and c_file.exists():
                self.preprocessor.load(p_file)
                self.supervised_detector.load(x_file)
                self.isolation_forest.load(i_file)
                self.clusterer.load(c_file)
                self.explainer = ForensicExplainer(self.supervised_detector)
                self.is_ready = True
                logger.info("Successfully loaded offline model artifacts from disk.")
                return True
        except Exception as e:
            logger.warning(f"Could not load pre-existing model artifacts: {e}")
        return False

    def run_inference_pipeline(
        self,
        X: pd.DataFrame,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[int, Dict[str, Any]]]:
        """
        Run inference across all models:
        Returns:
            model_probs: XGBoost suspicious probabilities
            anomaly_scores: Isolation Forest anomaly scores (0-1)
            is_anomaly: boolean anomaly flags
            cluster_labels: DBSCAN cluster IDs
            pca_coords: 2D coordinates for visual cluster plot
            cluster_summaries: cluster profile metadata
        """
        if not self.supervised_detector.is_fitted:
            # Fit on incoming batch if not previously fitted
            dummy_y = np.zeros(len(X))
            self.train_and_save_all(X, dummy_y)

        model_probs = self.supervised_detector.predict_probability(X)
        anomaly_scores, is_anomaly = self.isolation_forest.predict_anomaly_scores(X)
        cluster_labels, pca_coords, cluster_summaries = self.clusterer.fit_predict(X)

        return (
            model_probs,
            anomaly_scores,
            is_anomaly,
            cluster_labels,
            pca_coords,
            cluster_summaries,
        )
