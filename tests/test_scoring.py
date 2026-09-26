"""Tests for risk fusion engine, confidence calibration, and alert ranking."""
import pytest
from scoring.risk_engine import RiskEngine
from scoring.confidence import ConfidenceCalculator
from scoring.alert_ranker import AlertRanker
from core.enums import PriorityLevel, EvidenceStrength


def test_risk_engine_fusion():
    engine = RiskEngine(
        weight_model=0.35,
        weight_anomaly=0.25,
        weight_graph=0.20,
        weight_network=0.20,
    )

    eval_result = engine.evaluate_risk(
        model_prob=0.90,
        anomaly_score=0.85,
        graph_signal=0.75,
        network_signal=0.60,
    )

    score = eval_result["risk_score"]
    assert 0.0 <= score <= 100.0
    assert score > 70.0  # High inputs should yield high risk score
    assert len(eval_result["reasons"]) > 0


def test_confidence_and_strength():
    conf, strength = ConfidenceCalculator.calculate_confidence_and_strength(
        model_prob=0.85,
        anomaly_score=0.88,
        tx_count=12,
        supporting_records_count=12,
        has_network_observation=True,
    )

    assert 0.0 <= conf <= 1.0
    assert conf >= 0.75
    assert strength == EvidenceStrength.HIGH


def test_alert_prioritization():
    assert AlertRanker.determine_priority(90.0) == PriorityLevel.CRITICAL
    assert AlertRanker.determine_priority(70.0) == PriorityLevel.HIGH
    assert AlertRanker.determine_priority(50.0) == PriorityLevel.MEDIUM
    assert AlertRanker.determine_priority(20.0) == PriorityLevel.LOW
