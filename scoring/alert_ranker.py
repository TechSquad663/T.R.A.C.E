"""Alert ranking and prioritization engine."""
from typing import List, Dict, Any, Optional
from core.enums import PriorityLevel, NodeType
from core.models import Alert, Entity
from core.utils import parse_timestamp_iso
from datetime import datetime, timezone


class AlertRanker:
    """Ranks and prioritizes investigative leads according to fused risk and evidentiary confidence."""

    @staticmethod
    def determine_priority(risk_score: float) -> PriorityLevel:
        if risk_score >= 80.0:
            return PriorityLevel.CRITICAL
        elif risk_score >= 65.0:
            return PriorityLevel.HIGH
        elif risk_score >= 45.0:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW

    def rank_alerts(
        self,
        entities: Dict[str, Entity],
        combined_evidences: Dict[str, Dict[str, Any]],
        risk_evaluations: Dict[str, Dict[str, Any]],
        confidence_results: Dict[str, Any],
    ) -> List[Alert]:
        """Generate, rank, and prioritize alerts for analysts."""
        alerts: List[Alert] = []

        for ent_id, entity in entities.items():
            risk_eval = risk_evaluations.get(ent_id, {})
            risk_score = risk_eval.get("risk_score", entity.risk_score)
            priority = self.determine_priority(risk_score)

            conf_tuple = confidence_results.get(ent_id, (0.75, "MODERATE"))
            conf_val, strength = conf_tuple[0], conf_tuple[1]

            evidence = combined_evidences.get(ent_id, {})

            # Concise, professional forensic pattern classification
            pattern_str = "Standard Activity"
            m_p = risk_eval.get("model_probability", entity.model_probability)
            a_s = risk_eval.get("anomaly_score", entity.anomaly_score)
            g_s = risk_eval.get("graph_signal", 0.0)
            n_s = risk_eval.get("network_signal", 0.0)
            graph_ev = evidence.get("graph_evidence", {})
            fan_in = graph_ev.get("fan_in_ratio", 0.0)
            fan_out = graph_ev.get("fan_out_ratio", 0.0)

            if fan_in >= 0.70:
                pattern_str = "Fan-In Consolidation"
            elif fan_out >= 0.70:
                pattern_str = "Fan-Out Dispersion"
            elif len(entity.ips) >= 3:
                pattern_str = "Multi-IP Association"
            elif m_p >= 0.70:
                pattern_str = "High-Risk Classifier"
            elif a_s >= 0.75:
                pattern_str = "Statistical Anomaly"
            elif g_s >= 0.60:
                pattern_str = "Topological Hub"
            elif n_s >= 0.50:
                pattern_str = "Cross-Border Relay"
            elif risk_score >= 65.0:
                pattern_str = "Elevated Risk Flow"
            elif risk_score >= 45.0:
                pattern_str = "Moderate Activity"
            else:
                pattern_str = "Routine Transfer"

            reasons = risk_eval.get("reasons", ["Routine transaction volume"])

            alert_id = f"ALT_{ent_id[:12]}"
            alert = Alert(
                alert_id=alert_id,
                entity_id=ent_id,
                entity_type=entity.entity_type,
                risk_score=risk_score,
                confidence=conf_val,
                priority=priority,
                timestamp=datetime.now(timezone.utc).isoformat(),
                pattern=pattern_str,
                reasons=reasons,
                model_evidence=evidence.get("model_evidence", {}),
                graph_evidence=evidence.get("graph_evidence", {}),
                network_evidence=evidence.get("network_evidence", {}),
                transaction_evidence=evidence.get("transaction_evidence", {}),
                related_transactions=entity.txids,
                related_ips=entity.ips,
                cluster_id=entity.cluster_id,
                evidence_strength=strength,
            )
            alerts.append(alert)

        # Sort descending by risk_score and confidence
        alerts.sort(key=lambda a: (a.risk_score, a.confidence), reverse=True)
        return alerts
