"""Tests for feature engineering and ground truth isolation."""
import pytest
from core.models import TransactionRecord, Entity
from features.temporal import extract_temporal_features
from features.network import extract_network_features
from features.feature_pipeline import FeaturePipeline, FEATURE_COLUMNS


def test_temporal_features():
    timestamps = [
        "2026-03-01T10:00:00Z",
        "2026-03-01T10:00:05Z",
        "2026-03-01T10:00:10Z",
    ]
    feats = extract_temporal_features(timestamps)
    assert feats["tx_velocity_per_hour"] > 0
    assert "burst_score" in feats


def test_network_features():
    obs = [
        {"src_ip": "1.1.1.1", "dst_ip": "2.2.2.2", "src_port": 8333, "geo_country": "US", "asn": "AS15169"},
        {"src_ip": "3.3.3.3", "dst_ip": "2.2.2.2", "src_port": 8333, "geo_country": "DE", "asn": "AS24940"},
    ]
    feats = extract_network_features(obs)
    assert feats["unique_source_ips"] == 2.0
    assert feats["unique_countries"] == 2.0


def test_ground_truth_isolation():
    """Verify that NO ground truth field or scenario identifier leaks into feature columns."""
    forbidden = ["ground_truth", "label", "scenario", "target", "class", "is_suspicious"]
    for col in FEATURE_COLUMNS:
        for f in forbidden:
            assert f not in col.lower(), f"Potential ground-truth leakage detected in feature: {col}"
