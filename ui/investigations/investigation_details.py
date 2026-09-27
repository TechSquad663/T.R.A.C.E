"""Analyst case details editor and evidence attachment workspace with responsive scroll layout."""
from datetime import datetime, timezone
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QFrame, QScrollArea, QWidget, QMessageBox
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
from core.models import InvestigationCase
from core.enums import PriorityLevel, InvestigationStatus


from ui.components import ForensicComboBox


class CaseDetailsDialog(QDialog):
    """Case editor modal for analyst notes and evidence management."""

    def __init__(self, case: InvestigationCase, parent=None):
        super().__init__(parent)
        self.case = case
        self.case_deleted = False
        self.setWindowTitle(f"Case File — {case.case_id}: {case.title}")
        self.resize(720, 560)
        self.setMinimumSize(580, 420)
        self.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; color: {THEME_COLORS['text_primary']};")

        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(16, 16, 16, 16)
        dialog_layout.setSpacing(12)

        # Header Title
        title_lbl = QLabel(f"CASE WORKSPACE [{case.case_id}]")
        title_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        dialog_layout.addWidget(title_lbl)

        # Scroll Area for Form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(12)

        # Fields Frame
        form_frame = QFrame()
        form_frame.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 14px;")
        f_layout = QVBoxLayout(form_frame)
        f_layout.setSpacing(10)

        # Title
        f_layout.addWidget(QLabel("Case Title:"))
        self.title_input = QLineEdit(case.title)
        f_layout.addWidget(self.title_input)

        # Status & Priority
        sp_box = QHBoxLayout()
        sp_box.addWidget(QLabel("Status:"))
        self.status_combo = ForensicComboBox()
        self.status_combo.addItems([s.value for s in InvestigationStatus])
        self.status_combo.setCurrentText(case.status.value)
        sp_box.addWidget(self.status_combo)

        sp_box.addWidget(QLabel("Priority:"))
        self.prio_combo = ForensicComboBox()
        self.prio_combo.addItems([p.value for p in PriorityLevel])
        self.prio_combo.setCurrentText(case.priority.value)
        sp_box.addWidget(self.prio_combo)
        f_layout.addLayout(sp_box)

        # Notes
        f_layout.addWidget(QLabel("Analyst Case Notes & Evidence Findings:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlainText(case.analyst_notes)
        self.notes_edit.setPlaceholderText("Record evidentiary corroboration, subpoenas, or analyst conclusions...")
        self.notes_edit.setMinimumHeight(140)
        f_layout.addWidget(self.notes_edit)

        layout.addWidget(form_frame)

        # Attached Items Summary
        att_lbl = QLabel(f"Attached Subject Entity: <b>{case.subject_entity_id}</b>  |  Linked Alerts: <b>{len(case.attached_alerts)}</b>  |  Transactions: <b>{len(case.attached_txids)}</b>")
        att_lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")
        layout.addWidget(att_lbl)

        scroll.setWidget(content)
        dialog_layout.addWidget(scroll, 1)

        # Buttons
        btn_box = QHBoxLayout()

        btn_delete = QPushButton("🗑️ Delete Case")
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {THEME_COLORS['accent_red']};
                color: {THEME_COLORS['accent_red']};
                padding: 6px 14px;
                border-radius: 4px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['accent_red']};
                color: #FFFFFF;
            }}
        """)
        btn_delete.clicked.connect(self._delete_case)
        btn_box.addWidget(btn_delete)
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border_light']};
                color: {THEME_COLORS['text_primary']};
                padding: 6px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['bg_card_alt']};
            }}
        """)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("Save Case File")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['accent_blue']};
                color: white;
                padding: 6px 18px;
                border: none;
                border-radius: 4px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: #1D4ED8;
            }}
        """)
        btn_save.clicked.connect(self._save_case)
        btn_box.addWidget(btn_save)

        dialog_layout.addLayout(btn_box)

    def _save_case(self):
        self.case.title = self.title_input.text().strip() or "Untitled Case"
        self.case.status = InvestigationStatus(self.status_combo.currentText())
        self.case.priority = PriorityLevel(self.prio_combo.currentText())
        self.case.analyst_notes = self.notes_edit.toPlainText()
        self.case.updated_at = datetime.now(timezone.utc).isoformat()
        self.accept()

    def _delete_case(self):
        reply = QMessageBox.question(
            self,
            "Confirm Case Deletion",
            f"Are you sure you want to permanently delete case {self.case.case_id}?\n\nThis will remove the case docket and all associated analyst notes from the database.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.case_deleted = True
            self.accept()
