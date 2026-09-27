"""Investigations Workspace Page for case file tracking with search filtering and robust selection."""
import uuid
from datetime import datetime, timezone
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QLineEdit, QScrollArea, QMenu
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
from core.models import InvestigationCase
from core.enums import PriorityLevel, InvestigationStatus
from core.database import TRACEDatabase
from .investigation_details import CaseDetailsDialog
from ui.components import ForensicComboBox, setup_table_headers


class InvestigationsPage(QWidget):
    """Analyst workspace for organizing leads into formal investigation cases."""

    def __init__(self):
        super().__init__()
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Title & New Case Button
        header_box = QHBoxLayout()
        title_box = QVBoxLayout()
        self.title = QLabel("INVESTIGATION WORKSPACE & CASE DOCKETS")
        self.subtitle = QLabel("Manage forensic case files, record analyst corroboration notes, and attach evidence leads. Double-click to edit docket.")
        self.subtitle.setWordWrap(True)
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        header_box.addLayout(title_box)
        header_box.addStretch()

        self.btn_new_case = QPushButton("➕ Create New Case")
        self.btn_new_case.setCursor(Qt.PointingHandCursor)
        self.btn_new_case.clicked.connect(self._create_new_case)
        header_box.addWidget(self.btn_new_case)

        self.btn_delete_case = QPushButton("🗑️ Delete Case")
        self.btn_delete_case.setCursor(Qt.PointingHandCursor)
        self.btn_delete_case.clicked.connect(self._delete_selected_case)
        header_box.addWidget(self.btn_delete_case)

        layout.addLayout(header_box)

        # Filter & Search Bar
        self.filter_bar = QFrame()
        fb_layout = QHBoxLayout(self.filter_bar)
        fb_layout.setContentsMargins(8, 6, 8, 6)
        fb_layout.setSpacing(12)

        fb_layout.addWidget(QLabel("Status:"))
        self.status_filter = ForensicComboBox()
        self.status_filter.addItem("All Statuses")
        for s in InvestigationStatus:
            self.status_filter.addItem(s.value)
        self.status_filter.currentTextChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.status_filter)

        fb_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Case ID, title, or subject entity...")
        self.search_input.textChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.search_input, 1)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self._reset_filters)
        fb_layout.addWidget(self.btn_reset)

        layout.addWidget(self.filter_bar)

        # Cases Table
        self.cases_table = QTableWidget(0, 6)
        setup_table_headers(self.cases_table)
        self.cases_table.setHorizontalHeaderLabels([
            "Case ID", "Title", "Subject Entity", "Priority", "Status", "Last Updated"
        ])
        header = self.cases_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self.cases_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cases_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cases_table.setMinimumHeight(280)
        self.cases_table.doubleClicked.connect(self._open_case_details)
        self.cases_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.cases_table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.cases_table, 1)

        scroll.setWidget(content)
        page_layout.addWidget(scroll)

        self.db = TRACEDatabase()
        self.cases: list[InvestigationCase] = []
        self.filtered_cases: list[InvestigationCase] = []
        self._init_sample_cases()

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update element styling according to active theme."""
        is_dark = theme_manager.is_dark()
        self.title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        self.filter_bar.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 6px 12px;")
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
        self.btn_delete_case.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {THEME_COLORS['accent_red']};
                color: {THEME_COLORS['accent_red']};
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['accent_red']};
                color: #FFFFFF;
            }}
        """)

    def _init_sample_cases(self):
        """Populate baseline cases from SQLite or initialize sample defaults."""
        existing = self.db.load_cases()
        if existing:
            self.cases = existing
        else:
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
            self.db.save_cases(self.cases)
        self.filtered_cases = list(self.cases)
        self._populate_table()

    def update_data(self, pipeline):
        """Generate case files and synchronize from pipeline alerts into database."""
        if not pipeline or not pipeline.alerts:
            return
        now = datetime.now(timezone.utc).isoformat()
        existing_ids = {c.case_id for c in self.cases}
        new_cases = []
        for i, alert in enumerate(pipeline.alerts[:5]):
            cid = f"CAS-2026-{alert.alert_id[-4:]}"
            if cid in existing_ids:
                continue
            c = InvestigationCase(
                case_id=cid,
                title=f"Flagged Lead: {alert.pattern} ({alert.entity_id[:16]})",
                subject_entity_id=alert.entity_id,
                priority=alert.priority,
                status=InvestigationStatus.OPEN if i == 0 else InvestigationStatus.UNDER_REVIEW,
                created_at=alert.timestamp or now,
                updated_at=now,
                analyst_notes=f"Generated from lead {alert.alert_id}. Risk score: {alert.risk_score:.1f}. Reasons: {', '.join(alert.reasons[:2])}",
                attached_txids=alert.related_transactions[:5],
                attached_alerts=[alert.alert_id],
            )
            new_cases.append(c)
            self.db.save_case(c)
        if new_cases:
            self.cases = new_cases + self.cases
            self.filtered_cases = list(self.cases)
            self._populate_table()

    def _populate_table(self):
        self.cases_table.setRowCount(0)
        for i, c in enumerate(self.filtered_cases):
            self.cases_table.insertRow(i)
            item_id = QTableWidgetItem(c.case_id)
            item_id.setToolTip(f"Double-click to open and edit case file {c.case_id}")
            self.cases_table.setItem(i, 0, item_id)
            self.cases_table.setItem(i, 1, QTableWidgetItem(c.title))
            self.cases_table.setItem(i, 2, QTableWidgetItem(c.subject_entity_id))
            self.cases_table.setItem(i, 3, QTableWidgetItem(c.priority.value))
            self.cases_table.setItem(i, 4, QTableWidgetItem(c.status.value))
            self.cases_table.setItem(i, 5, QTableWidgetItem(c.updated_at[:19]))

    def _apply_filters(self):
        stat = self.status_filter.currentText()
        q = self.search_input.text().strip().lower()

        filtered = [
            c for c in self.cases
            if (stat == "All Statuses" or c.status.value == stat)
            and (not q or q in c.case_id.lower() or q in c.title.lower() or q in c.subject_entity_id.lower())
        ]
        self.filtered_cases = filtered
        self._populate_table()

    def _reset_filters(self):
        self.status_filter.setCurrentIndex(0)
        self.search_input.clear()
        self.filtered_cases = list(self.cases)
        self._populate_table()

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
        self.db.save_case(new_case)
        self._apply_filters()
        QMessageBox.information(self, "Case Docket Created", f"New case dossier {cid} created and saved to database successfully.")

    def _delete_selected_case(self):
        selected_indexes = self.cases_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "No Case Selected", "Please select a case row from the table to delete.")
            return
        row = selected_indexes[0].row()
        if 0 <= row < len(self.filtered_cases):
            case = self.filtered_cases[row]
            reply = QMessageBox.question(
                self,
                "Confirm Case Deletion",
                f"Are you sure you want to permanently delete case {case.case_id} ('{case.title}')?\n\nThis will remove the case docket and all analyst notes from the database.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.db.delete_case(case.case_id)
                if case in self.cases:
                    self.cases.remove(case)
                self._apply_filters()
                QMessageBox.information(self, "Case Deleted", f"Case {case.case_id} has been permanently deleted from storage.")

    def _show_context_menu(self, pos):
        item = self.cases_table.itemAt(pos)
        if not item:
            return
        row = item.row()
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border']};
                color: {THEME_COLORS['text_primary']};
                padding: 4px;
            }}
            QMenu::item:selected {{
                background-color: {THEME_COLORS['accent_blue']};
                color: #FFFFFF;
            }}
        """)
        action_open = menu.addAction("🔍 Open Case Dossier")
        action_delete = menu.addAction("🗑️ Delete Case")
        action = menu.exec(self.cases_table.viewport().mapToGlobal(pos))
        if action == action_open:
            self._open_case_details(self.cases_table.model().index(row, 0))
        elif action == action_delete:
            self.cases_table.selectRow(row)
            self._delete_selected_case()

    def _open_case_details(self, index):
        row = index.row()
        if 0 <= row < len(self.filtered_cases):
            case = self.filtered_cases[row]
            dialog = CaseDetailsDialog(case, parent=self)
            if dialog.exec():
                if getattr(dialog, "case_deleted", False):
                    self.db.delete_case(case.case_id)
                    if case in self.cases:
                        self.cases.remove(case)
                    self._apply_filters()
                    QMessageBox.information(self, "Case Deleted", f"Case {case.case_id} has been permanently deleted from storage.")
                else:
                    self.db.save_case(case)
                    self._populate_table()
