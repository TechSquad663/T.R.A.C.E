"""JSON export utilities for forensic dockets and cases."""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Union
from core.models import InvestigationCase

logger = logging.getLogger("TRACE.JSONExport")


def export_docket_to_json(docket: Dict[str, Any], output_path: Union[str, Path]):
    """Export complete evidence docket to JSON."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(docket, f, indent=2)


def export_investigation_case_json(case: InvestigationCase, output_path: Union[str, Path]):
    """Export investigation case file to JSON."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump({
            "case_id": case.case_id,
            "title": case.title,
            "subject_entity_id": case.subject_entity_id,
            "priority": case.priority.value,
            "status": case.status.value,
            "created_at": case.created_at,
            "updated_at": case.updated_at,
            "analyst_notes": case.analyst_notes,
            "attached_txids": case.attached_txids,
            "attached_alerts": case.attached_alerts,
        }, f, indent=2)
