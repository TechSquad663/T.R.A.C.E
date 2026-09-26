"""Comprehensive forensic evidence dossier builder."""
import logging
from typing import Dict, Any, List, Optional
from core.models import Entity, Alert, TransactionRecord
from core.constants import DISCLAIMER_TEXT, STATUS_DESCRIPTIONS
from .evidence_paths import EvidencePathExtractor

logger = logging.getLogger("TRACE.EvidenceBuilder")


class EvidenceBuilder:
    """Builds a structured forensic evidence dossier for any investigated entity."""

    def __init__(self, graph, model_manager):
        self.graph = graph
        self.model_manager = model_manager
        self.path_extractor = EvidencePathExtractor(graph)

    def build_docket(
        self,
        entity: Entity,
        alert: Optional[Alert] = None,
        records: Optional[List[TransactionRecord]] = None,
    ) -> Dict[str, Any]:
        """Construct full evidence dossier for analyst review."""
        path_chain = self.path_extractor.trace_entity_chain(
            entity_addresses=entity.addresses,
            entity_ips=entity.ips,
        )

        return {
            "entity_id": entity.entity_id,
            "entity_type": entity.entity_type.value,
            "addresses": entity.addresses,
            "associated_ips": entity.ips,
            "risk_score": entity.risk_score,
            "priority": entity.priority.value,
            "confidence": entity.confidence,
            "model_probability": entity.model_probability,
            "anomaly_score": entity.anomaly_score,
            "cluster_id": entity.cluster_id,
            "reasons": entity.reasons,
            "top_contributing_features": entity.top_contributing_features,
            "evidence_chain": path_chain,
            "transaction_count": entity.transaction_count,
            "total_in_btc": entity.total_in,
            "total_out_btc": entity.total_out,
            "fan_in_ratio": entity.fan_in_ratio,
            "fan_out_ratio": entity.fan_out_ratio,
            "burstiness": entity.burstiness,
            "velocity": entity.velocity,
            "legal_disclaimer": DISCLAIMER_TEXT,
        }
