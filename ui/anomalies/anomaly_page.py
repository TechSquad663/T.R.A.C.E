"""Behavioral Anomalies page displaying Isolation Forest deviations and pattern filters."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QPushButton
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS
from core.models import Entity


class AnomalyPage(QWidget):
    """Forensic anomalies station highlighting statistical outliers and behavioral deviations."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Title
        title_box = QVBoxLayout()
        title = QLabel("BEHAVIORAL ANOMALIES & UNSUPERVISED OUTLIERS")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        subtitle = QLabel("Isolation Forest multivariate statistical outliers classified across behavioral deviation archetypes.")
        subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        # Filters Bar
        filter_bar = QFrame()
        filter_bar.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 8px 12px;")
        fb_layout = QHBoxLayout(filter_bar)
        fb_layout.setContentsMargins(6, 4, 6, 4)
        fb_layout.setSpacing(12)

        fb_layout.addWidget(QLabel("Pattern Archetype:"))
        self.pattern_filter = QComboBox()
        self.pattern_filter.addItems([
            "All Behavioral Patterns",
            "Temporal Burst",
            "High Fan-Out",
            "High Fan-In",
            "Multi-IP Association",
            "Multi-Country Relay",
            "Rapid Chain",
            "Dormant Activation",
        ])
        self.pattern_filter.currentTextChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.pattern_filter)

        fb_layout.addWidget(QLabel("Min Anomaly Score:"))
        self.score_filter = QComboBox()
        self.score_filter.addItems(["All Deviations (>= 0.0)", "Elevated (>= 0.50)", "High Outliers (>= 0.75)", "Severe (>= 0.85)"])
        self.score_filter.currentTextChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.score_filter)

        fb_layout.addStretch()
        layout.addWidget(filter_bar)

        # Anomalies Table
        self.anomaly_table = QTableWidget(0, 7)
        self.anomaly_table.setHorizontalHeaderLabels([
            "Entity ID", "Anomaly Score", "Model Prob", "Risk Score", "Detected Archetype", "Cohort", "Key Anomaly Drivers"
        ])
        self.anomaly_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.anomaly_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.anomaly_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.anomaly_table)

        self.entities: list[Entity] = []

    def update_data(self, pipeline):
        if not pipeline:
            return
        # Filter to entities with some deviation
        self.entities = sorted(pipeline.entities.values(), key=lambda e: e.anomaly_score, reverse=True)
        self._populate_table(self.entities)

    def _populate_table(self, entities):
        self.anomaly_table.setRowCount(0)
        for i, e in enumerate(entities[:200]):
            self.anomaly_table.insertRow(i)
            self.anomaly_table.setItem(i, 0, QTableWidgetItem(e.entity_id))
            self.anomaly_table.setItem(i, 1, QTableWidgetItem(f"{e.anomaly_score:.2f}"))
            self.anomaly_table.setItem(i, 2, QTableWidgetItem(f"{e.model_probability:.2f}"))
            self.anomaly_table.setItem(i, 3, QTableWidgetItem(f"{e.risk_score}/100"))

            pattern = e.reasons[0] if e.reasons else "Statistical Baseline"
            self.anomaly_table.setItem(i, 4, QTableWidgetItem(pattern))
            self.anomaly_table.setItem(i, 5, QTableWidgetItem(f"Cohort #{e.cluster_id}"))

            top_drivers = ", ".join(f.get("feature", "") for f in e.top_contributing_features[:2])
            self.anomaly_table.setItem(i, 6, QTableWidgetItem(top_drivers or "Standard flow"))

    def _apply_filters(self):
        pattern_sel = self.pattern_filter.currentText()
        score_sel = self.score_filter.currentText()

        min_score = 0.0
        if "0.50" in score_sel:
            min_score = 0.50
        elif "0.75" in score_sel:
            min_score = 0.75
        elif "0.85" in score_sel:
            min_score = 0.85

        filtered = [
            e for e in self.entities
            if e.anomaly_score >= min_score and (
                pattern_sel == "All Behavioral Patterns" or
                any(pattern_sel.lower() in r.lower() for r in e.reasons)
            )
        ]
        self._populate_table(filtered)
