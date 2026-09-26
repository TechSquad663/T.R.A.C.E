"""Analyst case details editor and evidence attachment workspace."""
from datetime import datetime, timezone
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QFrame, QListWidget
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS
from core.models import InvestigationCase
from core.enums import PriorityLevel, InvestigationStatus


class CaseDetailsDialog(QDialog):
    """Case editor modal for analyst notes and evidence management."""

    def __init__(self, case: InvestigationCase, parent=None):
        super().__init__(parent)
        self.case = case
        self.setWindowTitle(f"Case File — {case.case_id}: {case.title}")
        self.resize(700, 520)
        self.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; color: {THEME_COLORS['text_primary']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header Title
        title_lbl = QLabel(f"CASE WORKSPACE [{case.case_id}]")
        title_lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        layout.addWidget(title_lbl)

        # Fields Frame
        form_frame = QFrame()
        form_frame.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 12px;")
        f_layout = QVBoxLayout(form_frame)
        f_layout.setSpacing(10)

        # Title
        f_layout.addWidget(QLabel("Case Title:"))
        self.title_input = QLineEdit(case.title)
        f_layout.addWidget(self.title_input)

        # Status & Priority
        sp_box = QHBoxLayout()
        sp_box.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems([s.value for s in InvestigationStatus])
        self.status_combo.setCurrentText(case.status.value)
        sp_box.addWidget(self.status_combo)

        sp_box.addWidget(QLabel("Priority:"))
        self.prio_combo = QComboBox()
        self.prio_combo.addItems([p.value for p in PriorityLevel])
        self.prio_combo.setCurrentText(case.priority.value)
        sp_box.addWidget(self.prio_combo)
        f_layout.addLayout(sp_box)

        # Notes
        f_layout.addWidget(QLabel("Analyst Case Notes & Evidence Findings:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlainText(case.analyst_notes)
        self.notes_edit.setPlaceholderText("Record evidentiary corroboration, subpoenas, or analyst conclusions...")
        f_layout.addWidget(self.notes_edit)

        layout.addWidget(form_frame)

        # Attached Items Summary
        att_lbl = QLabel(f"Attached Entities: {case.subject_entity_id} | Alerts: {len(case.attached_alerts)}")
        att_lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")
        layout.addWidget(att_lbl)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("Save Case File")
        btn_save.setStyleSheet(f"background-color: {THEME_COLORS['accent_blue']}; color: white; padding: 6px 16px; border-radius: 4px; font-weight: 700;")
        btn_save.clicked.connect(self._save_case)
        btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    def _save_case(self):
        self.case.title = self.title_input.text().strip() or "Untitled Case"
        self.case.status = InvestigationStatus(self.status_combo.currentText())
        self.case.priority = PriorityLevel(self.prio_combo.currentText())
        self.case.analyst_notes = self.notes_edit.toPlainText()
        self.case.updated_at = datetime.now(timezone.utc).isoformat()
        self.accept()
