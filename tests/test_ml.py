"""Tests for Machine Learning, anomaly detection, and SHAP explainability."""
import pytest
import numpy as np
import pandas as pd
from ml.xgboost_detector import XGBoostDetector
from ml.isolation_forest import IsolationForestDetector
from ml.clustering import BehavioralClusterer
from ml.explainability import ForensicExplainer
from features.feature_pipeline import FEATURE_COLUMNS


@pytest.fixture
def sample_feature_df():
    np.random.seed(42)
    data = np.random.uniform(0.0, 10.0, size=(25, len(FEATURE_COLUMNS)))
    df = pd.DataFrame(data, columns=FEATURE_COLUMNS, index=[f"ENT_{i}" for i in range(25)])
    return df


def test_xgboost_detector(sample_feature_df):
    y = np.array([0] * 20 + [1] * 5)
    detector = XGBoostDetector()
    metrics = detector.train(sample_feature_df, y)
    assert metrics["training_accuracy"] >= 0.80

    probs = detector.predict_probability(sample_feature_df)
    assert len(probs) == len(sample_feature_df)
    assert all(0.0 <= p <= 1.0 for p in probs)


def test_isolation_forest(sample_feature_df):
    detector = IsolationForestDetector(contamination=0.1)
    scores, is_ano = detector.predict_anomaly_scores(sample_feature_df)
    assert len(scores) == len(sample_feature_df)
    assert len(is_ano) == len(sample_feature_df)
    assert all(0.0 <= s <= 1.0 for s in scores)


def test_behavioral_clusterer(sample_feature_df):
    clusterer = BehavioralClusterer(eps=1.5, min_samples=2)
    labels, coords, summaries = clusterer.fit_predict(sample_feature_df)
    assert len(labels) == len(sample_feature_df)
    assert coords.shape == (len(sample_feature_df), 2)
    assert len(summaries) >= 1


def test_forensic_explainer(sample_feature_df):
    y = np.array([0] * 20 + [1] * 5)
    detector = XGBoostDetector()
    detector.train(sample_feature_df, y)

    explainer = ForensicExplainer(detector)
    sample_row = sample_feature_df.iloc[0]
    top_features = explainer.explain_instance(sample_row, top_k=5)
    assert len(top_features) <= 5
    assert "feature" in top_features[0]
    assert "impact" in top_features[0]
