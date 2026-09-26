"""Investigations Workspace Page for case file tracking."""
import uuid
from datetime import datetime, timezone
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
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
        self.title = QLabel("INVESTIGATION WORKSPACE & CASE DOCKETS")
        self.subtitle = QLabel("Manage forensic case files, record analyst corroboration notes, and attach evidence leads.")
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        header_box.addLayout(title_box)
        header_box.addStretch()

        self.btn_new_case = QPushButton("➕ Create New Case")
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

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update element styling according to active theme."""
        is_dark = theme_manager.is_dark()
        self.title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        self.btn_new_case.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['accent_blue']};
                color: #FFFFFF;
                padding: 8px 18px;
                border: none;
                border-radius: 6px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {"#1D4ED8" if is_dark else "#0369A1"};
            }}
        """)

    def _init_sample_cases(self):
        """Populate initial baseline cases."""
        now = datetime.now(timezone.utc).isoformat()
        c1 = InvestigationCase(
            case_id="CAS-2026-081",
            title="High-Fanout Clustering around Exchange Gateway",
            subject_entity_id="ENT_WAL_3zTF",
            priority=PriorityLevel.CRITICAL,
            status=InvestigationStatus.OPEN,
            created_at=now,
            updated_at=now,
            analyst_notes="Rapid multi-hop disbursement observed following temporal burst. Correlation with AS13335 relay nodes.",
        )
        c2 = InvestigationCase(
            case_id="CAS-2026-082",
            title="Dormant Wallet Reactivation & Multi-Country Relay",
            subject_entity_id="ENT_WAL_7kLP",
            priority=PriorityLevel.HIGH,
            status=InvestigationStatus.UNDER_REVIEW,
            created_at=now,
            updated_at=now,
            analyst_notes="Entity inactive for >180 days reactivated with high volume broadcast across 4 geographic regions.",
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
        cid = f"CAS-2026-{uuid.uuid4().hex[:4].upper()}"
        now = datetime.now(timezone.utc).isoformat()
        new_case = InvestigationCase(
            case_id=cid,
            title="New Investigative Docket",
            subject_entity_id="ENT_WAL_PENDING",
            priority=PriorityLevel.MEDIUM,
            status=InvestigationStatus.OPEN,
            created_at=now,
            updated_at=now,
            analyst_notes="Case initiated.",
        )
        self.cases.insert(0, new_case)
        self._populate_table()
        QMessageBox.information(self, "Case Docket Created", f"New case dossier {cid} created successfully.")

    def _open_case_details(self, index):
        row = index.row()
        if row < len(self.cases):
            case = self.cases[row]
            dialog = CaseDetailsDialog(case, parent=self)
            if dialog.exec():
                self._populate_table()
