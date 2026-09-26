"""Confidence calculation and evidentiary strength calibration."""
from typing import Dict, Any, Tuple
from core.enums import EvidenceStrength


class ConfidenceCalculator:
    """Computes evidentiary strength and confidence indices independently from risk scores."""

    @staticmethod
    def calculate_confidence_and_strength(
        model_prob: float,
        anomaly_score: float,
        tx_count: int,
        supporting_records_count: int,
        has_network_observation: bool,
    ) -> Tuple[float, EvidenceStrength]:
        """
        Confidence measures reliability of observations (sample size, cross-layer corroboration).
        Evidence strength represents qualitative certainty.
        """
        # Base confidence from sample depth
        sample_score = min(1.0, tx_count / 10.0)

        # Cross-layer corroboration bonus (0 to 1)
        layer_bonus = 1.0 if has_network_observation else 0.2
        corroboration = 1.0 if supporting_records_count > 3 else 0.3

        # Agreement between supervised & unsupervised models (0 to 1)
        agreement = 1.0 - abs(model_prob - anomaly_score)

        raw_conf = (0.30 * agreement) + (0.30 * sample_score) + (0.20 * layer_bonus) + (0.20 * corroboration)
        confidence = round(min(0.98, max(0.40, raw_conf)), 2)

        # Determine evidence strength tier
        if confidence >= 0.75 and supporting_records_count >= 5:
            strength = EvidenceStrength.HIGH
        elif confidence >= 0.55:
            strength = EvidenceStrength.MODERATE
        else:
            strength = EvidenceStrength.LOW

        return confidence, strength
