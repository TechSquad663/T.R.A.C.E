"""Investigations Workspace Page for case file tracking."""
import uuid
from datetime import datetime, timezone
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS
from core.models import InvestigationCase
from core.enums import PriorityLevel, InvestigationStatus
from .investigation_details import CaseDetailsDialog


class InvestigationsPage(QWidget):
    """Analyst workspace for organizing leads into formal investigation cases."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Title & New Case Button
        header_box = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("INVESTIGATION WORKSPACE & CASE DOCKETS")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        subtitle = QLabel("Manage forensic case files, record analyst corroboration notes, and attach evidence leads.")
        subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_box.addLayout(title_box)
        header_box.addStretch()

        self.btn_new_case = QPushButton("➕ Create New Case")
        self.btn_new_case.setStyleSheet("background-color: #2563EB; color: white; padding: 8px 18px; border-radius: 6px; font-weight: 700;")
        self.btn_new_case.clicked.connect(self._create_new_case)
        header_box.addWidget(self.btn_new_case)

        layout.addLayout(header_box)

        # Cases Table
        self.cases_table = QTableWidget(0, 6)
        self.cases_table.setHorizontalHeaderLabels([
            "Case ID", "Title", "Subject Entity", "Priority", "Status", "Last Updated"
        ])
        self.cases_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cases_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cases_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cases_table.doubleClicked.connect(self._open_case_details)
        layout.addWidget(self.cases_table)

        self.cases: list[InvestigationCase] = []
        self._init_sample_cases()

    def _init_sample_cases(self):
        """Populate initial baseline cases."""
        now = datetime.now(timezone.utc).isoformat()
        c1 = InvestigationCase(
            case_id="CASE-2026-001",
            title="Rapid Peeling Chain & Multi-IP Relay Inquiry",
            subject_entity_id="ENT_CIO_fanout",
            priority=PriorityLevel.HIGH,
            status=InvestigationStatus.UNDER_REVIEW,
            created_at=now,
            updated_at=now,
            analyst_notes="Identified rapid fund dispersion into 16 disparate destination wallets via Hetzner AS24940 nodes.",
        )
        c2 = InvestigationCase(
            case_id="CASE-2026-002",
            title="Dormant UTXO Activation Triage",
            subject_entity_id="ENT_WAL_dormant",
            priority=PriorityLevel.CRITICAL,
            status=InvestigationStatus.OPEN,
            created_at=now,
            updated_at=now,
            analyst_notes="Prolonged 2-year dormant entity activated, transferring significant volume across jurisdictions.",
        )
        self.cases = [c1, c2]
        self._populate_table()

    def _populate_table(self):
        self.cases_table.setRowCount(0)
        for i, c in enumerate(self.cases):
            self.cases_table.insertRow(i)
            self.cases_table.setItem(i, 0, QTableWidgetItem(c.case_id))
            self.cases_table.setItem(i, 1, QTableWidgetItem(c.title))
            self.cases_table.setItem(i, 2, QTableWidgetItem(c.subject_entity_id))
            self.cases_table.setItem(i, 3, QTableWidgetItem(c.priority.value))
            self.cases_table.setItem(i, 4, QTableWidgetItem(c.status.value))
            self.cases_table.setItem(i, 5, QTableWidgetItem(c.updated_at[:19]))

    def _create_new_case(self):
        now = datetime.now(timezone.utc).isoformat()
        cid = f"CASE-{datetime.now().year}-{len(self.cases) + 1:03d}"
        new_case = InvestigationCase(
            case_id=cid,
            title="New Lead Investigation",
            subject_entity_id="Unassigned",
            priority=PriorityLevel.MEDIUM,
            status=InvestigationStatus.OPEN,
            created_at=now,
            updated_at=now,
        )
        dialog = CaseDetailsDialog(new_case, self)
        if dialog.exec():
            self.cases.append(new_case)
            self._populate_table()

    def _open_case_details(self, index):
        row = index.row()
        if row < len(self.cases):
            case = self.cases[row]
            dialog = CaseDetailsDialog(case, self)
            if dialog.exec():
                self._populate_table()
