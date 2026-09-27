"""Unit tests for TRACEDatabase persistence layer."""
import pytest
from pathlib import Path
from core.database import TRACEDatabase
from core.models import InvestigationCase
from core.enums import PriorityLevel, InvestigationStatus


def test_case_persistence_roundtrip(tmp_path: Path):
    db_file = tmp_path / "test_trace.db"
    db = TRACEDatabase(db_path=db_file)

    case1 = InvestigationCase(
        case_id="CAS-2026-TEST1",
        title="High Fan-Out Investigation",
        subject_entity_id="ENT_WAL_001",
        priority=PriorityLevel.CRITICAL,
        status=InvestigationStatus.OPEN,
        created_at="2026-09-27T12:00:00Z",
        updated_at="2026-09-27T12:00:00Z",
        analyst_notes="Suspicious fund dispersal across 15 clusters.",
        attached_txids=["tx001", "tx002"],
        attached_alerts=["alt001"],
    )

    db.save_case(case1)
    loaded = db.load_cases()
    assert len(loaded) == 1
    assert loaded[0].case_id == "CAS-2026-TEST1"
    assert loaded[0].priority == PriorityLevel.CRITICAL
    assert loaded[0].status == InvestigationStatus.OPEN
    assert loaded[0].analyst_notes == "Suspicious fund dispersal across 15 clusters."
    assert loaded[0].attached_txids == ["tx001", "tx002"]

    # Update case notes and status
    case1.status = InvestigationStatus.UNDER_REVIEW
    case1.analyst_notes = "Updated corroboration by senior analyst."
    db.save_case(case1)

    loaded_updated = db.load_cases()
    assert len(loaded_updated) == 1
    assert loaded_updated[0].status == InvestigationStatus.UNDER_REVIEW
    assert loaded_updated[0].analyst_notes == "Updated corroboration by senior analyst."

    # Delete case
    db.delete_case("CAS-2026-TEST1")
    assert len(db.load_cases()) == 0


def test_investigations_page_delete(monkeypatch, tmp_path: Path):
    import os
    from PySide6.QtWidgets import QApplication, QMessageBox
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance() or QApplication([])

    from ui.investigations.investigations_page import InvestigationsPage
    from ui.investigations.investigation_details import CaseDetailsDialog

    page = InvestigationsPage()
    initial_count = len(page.cases)
    assert initial_count >= 1

    # Simulate deleting the first case
    case_to_delete = page.cases[0]
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: None)

    page.cases_table.selectRow(0)
    page._delete_selected_case()
    assert len(page.cases) == initial_count - 1
    assert case_to_delete not in page.cases

