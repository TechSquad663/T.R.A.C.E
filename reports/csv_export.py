"""CSV export utilities for alerts and entities."""
import csv
import logging
from pathlib import Path
from typing import List, Union
from core.models import Alert, Entity

logger = logging.getLogger("TRACE.CSVExport")


def export_alerts_to_csv(alerts: List[Alert], output_path: Union[str, Path]):
    """Export ranked alerts to standard CSV."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "alert_id", "entity_id", "entity_type", "priority", "risk_score",
        "confidence", "pattern", "timestamp", "cluster_id", "reasons"
    ]
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for a in alerts:
            writer.writerow({
                "alert_id": a.alert_id,
                "entity_id": a.entity_id,
                "entity_type": a.entity_type.value,
                "priority": a.priority.value,
                "risk_score": a.risk_score,
                "confidence": a.confidence,
                "pattern": a.pattern,
                "timestamp": a.timestamp,
                "cluster_id": a.cluster_id,
                "reasons": "; ".join(a.reasons),
            })


def export_entities_to_csv(entities: List[Entity], output_path: Union[str, Path]):
    """Export entity intelligence to standard CSV."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "entity_id", "entity_type", "risk_score", "priority", "model_probability",
        "anomaly_score", "cluster_id", "transaction_count", "total_in", "total_out"
    ]
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in entities:
            writer.writerow({
                "entity_id": e.entity_id,
                "entity_type": e.entity_type.value,
                "risk_score": e.risk_score,
                "priority": e.priority.value,
                "model_probability": e.model_probability,
                "anomaly_score": e.anomaly_score,
                "cluster_id": e.cluster_id,
                "transaction_count": e.transaction_count,
                "total_in": e.total_in,
                "total_out": e.total_out,
            })
