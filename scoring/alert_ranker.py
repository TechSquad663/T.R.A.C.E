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

            # Primary pattern description
            pattern_str = "Standard Activity"
            reasons = risk_eval.get("reasons", ["Routine transaction volume"])
            if reasons:
                pattern_str = reasons[0]

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
