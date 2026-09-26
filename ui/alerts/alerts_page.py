"""Ranked Alerts and lead prioritization page with responsive filtering and error-safe row selection."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from app.theme import THEME_COLORS, theme_manager
from core.models import Alert
from .alert_details import AlertDetailsDialog
from ui.components import ForensicComboBox


class AlertsPage(QWidget):
    """Ranked investigative alerts dashboard sorted by risk priority."""

    alert_selected = Signal(object)  # Alert instance

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

        # Header Title
        title_box = QVBoxLayout()
        self.title = QLabel("RANKED INVESTIGATIVE LEADS & ALERTS")
        self.subtitle = QLabel("Triage queue prioritizing entities exhibiting statistically severe behavioral deviations. Double-click any row to view forensic dossier.")
        self.subtitle.setWordWrap(True)
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        layout.addLayout(title_box)

        # Filters Bar
        self.filter_bar = QFrame()
        fb_layout = QHBoxLayout(self.filter_bar)
        fb_layout.setContentsMargins(8, 6, 8, 6)
        fb_layout.setSpacing(12)

        fb_layout.addWidget(QLabel("Priority Filter:"))
        self.priority_filter = ForensicComboBox()
        self.priority_filter.addItems(["All Priority Tiers", "Critical", "High", "Medium", "Low"])
        self.priority_filter.currentTextChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.priority_filter)

        fb_layout.addWidget(QLabel("Search:"))
        self.search_alert = QLineEdit()
        self.search_alert.setPlaceholderText("Search by Entity ID or pattern description...")
        self.search_alert.textChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.search_alert, 1)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self._reset_filters)
        fb_layout.addWidget(self.btn_reset)

        layout.addWidget(self.filter_bar)

        # Alerts Table
        self.alerts_table = QTableWidget(0, 8)
        self.alerts_table.setHorizontalHeaderLabels([
            "Priority", "Entity ID", "Risk Score", "Confidence", "Anomaly Score", "Model Prob", "Primary Pattern", "Timestamp"
        ])
        header = self.alerts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)

        self.alerts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.alerts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alerts_table.setMinimumHeight(300)
        self.alerts_table.doubleClicked.connect(self._open_alert_details)
        layout.addWidget(self.alerts_table, 1)

        scroll.setWidget(content)
        page_layout.addWidget(scroll)

        self.alerts: list[Alert] = []
        self.filtered_alerts: list[Alert] = []

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update element styling according to active theme."""
        self.title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        self.filter_bar.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 6px 12px;")

    def update_data(self, pipeline):
        if not pipeline:
            return
        self.alerts = pipeline.alerts
        self.filtered_alerts = list(self.alerts)
        self._populate_table(self.filtered_alerts)

    def _populate_table(self, alerts):
        self.alerts_table.setRowCount(0)
        for i, a in enumerate(alerts):
            self.alerts_table.insertRow(i)
            item_prio = QTableWidgetItem(a.priority.value)
            self.alerts_table.setItem(i, 0, item_prio)

            item_ent = QTableWidgetItem(a.entity_id)
            item_ent.setToolTip(f"Double-click to open full lead dossier for {a.entity_id}")
            self.alerts_table.setItem(i, 1, item_ent)

            self.alerts_table.setItem(i, 2, QTableWidgetItem(f"{a.risk_score:.1f}/100"))
            self.alerts_table.setItem(i, 3, QTableWidgetItem(f"{int(a.confidence * 100)}% ({a.evidence_strength.value})"))
            self.alerts_table.setItem(i, 4, QTableWidgetItem(f"{a.model_evidence.get('anomaly_score', 0.0):.2f}"))
            self.alerts_table.setItem(i, 5, QTableWidgetItem(f"{a.model_evidence.get('model_probability', 0.0):.2f}"))
            self.alerts_table.setItem(i, 6, QTableWidgetItem(a.pattern))
            self.alerts_table.setItem(i, 7, QTableWidgetItem(a.timestamp[:19] if a.timestamp else "N/A"))

    def _apply_filters(self):
        prio_sel = self.priority_filter.currentText()
        q = self.search_alert.text().strip().lower()

        self.filtered_alerts = [
            a for a in self.alerts
            if (prio_sel == "All Priority Tiers" or a.priority.value == prio_sel)
            and (not q or q in a.entity_id.lower() or q in a.pattern.lower())
        ]
        self._populate_table(self.filtered_alerts)

    def _reset_filters(self):
        self.priority_filter.setCurrentIndex(0)
        self.search_alert.clear()
        self.filtered_alerts = list(self.alerts)
        self._populate_table(self.filtered_alerts)

    def _open_alert_details(self, index):
        row = index.row()
        if 0 <= row < len(self.filtered_alerts):
            alert = self.filtered_alerts[row]
            dialog = AlertDetailsDialog(alert, parent=self)
            dialog.exec()
