"""Ranked Alerts and lead prioritization page."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QPushButton
)
from PySide6.QtCore import Qt, Signal
from app.theme import THEME_COLORS, theme_manager
from core.models import Alert
from .alert_details import AlertDetailsDialog


class AlertsPage(QWidget):
    """Ranked investigative alerts dashboard sorted by risk priority."""

    alert_selected = Signal(object)  # Alert instance

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Title
        title_box = QVBoxLayout()
        self.title = QLabel("RANKED INVESTIGATIVE LEADS & ALERTS")
        self.subtitle = QLabel("Triage queue prioritizing entities exhibiting statistically severe behavioral deviations.")
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        layout.addLayout(title_box)

        # Filters Bar
        self.filter_bar = QFrame()
        fb_layout = QHBoxLayout(self.filter_bar)
        fb_layout.setContentsMargins(6, 4, 6, 4)
        fb_layout.setSpacing(12)

        fb_layout.addWidget(QLabel("Priority Filter:"))
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["All Priority Tiers", "Critical", "High", "Medium", "Low"])
        self.priority_filter.currentTextChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.priority_filter)

        fb_layout.addStretch()

        self.search_alert = QLineEdit()
        self.search_alert.setPlaceholderText("Search by Entity ID or pattern description...")
        self.search_alert.textChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.search_alert)

        layout.addWidget(self.filter_bar)

        # Alerts Table
        self.alerts_table = QTableWidget(0, 8)
        self.alerts_table.setHorizontalHeaderLabels([
            "Priority", "Entity ID", "Risk Score", "Confidence", "Anomaly Score", "Model Prob", "Primary Pattern", "Timestamp"
        ])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alerts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.alerts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alerts_table.doubleClicked.connect(self._open_alert_details)
        layout.addWidget(self.alerts_table)

        self.alerts: list[Alert] = []

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update element styling according to active theme."""
        self.title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        self.filter_bar.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 8px 12px;")

    def update_data(self, pipeline):
        if not pipeline:
            return
        self.alerts = pipeline.alerts
        self._populate_table(self.alerts)

    def _populate_table(self, alerts):
        self.alerts_table.setRowCount(0)
        for i, a in enumerate(alerts):
            self.alerts_table.insertRow(i)
            self.alerts_table.setItem(i, 0, QTableWidgetItem(a.priority.value))
            self.alerts_table.setItem(i, 1, QTableWidgetItem(a.entity_id))
            self.alerts_table.setItem(i, 2, QTableWidgetItem(f"{a.risk_score}/100"))
            self.alerts_table.setItem(i, 3, QTableWidgetItem(f"{int(a.confidence * 100)}% ({a.evidence_strength.value})"))
            self.alerts_table.setItem(i, 4, QTableWidgetItem(f"{a.model_evidence.get('anomaly_score', 0.0):.2f}"))
            self.alerts_table.setItem(i, 5, QTableWidgetItem(f"{a.model_evidence.get('model_probability', 0.0):.2f}"))
            self.alerts_table.setItem(i, 6, QTableWidgetItem(a.pattern))
            self.alerts_table.setItem(i, 7, QTableWidgetItem(a.timestamp[:19]))

    def _apply_filters(self):
        prio_sel = self.priority_filter.currentText()
        q = self.search_alert.text().strip().lower()

        filtered = [
            a for a in self.alerts
            if (prio_sel == "All Priority Tiers" or a.priority.value == prio_sel)
            and (not q or q in a.entity_id.lower() or q in a.pattern.lower())
        ]
        self._populate_table(filtered)

    def _open_alert_details(self, index):
        row = index.row()
        if row < len(self.alerts):
            alert = self.alerts[row]
            dialog = AlertDetailsDialog(alert, parent=self)
            dialog.exec()
