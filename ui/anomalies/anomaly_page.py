"""Behavioral Anomalies page displaying Isolation Forest deviations and pattern filters."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
from core.models import Entity
from ui.entities.entity_details import EntityDetailsDialog
from ui.components import ForensicComboBox


class AnomalyPage(QWidget):
    """Forensic anomalies station highlighting statistical outliers and behavioral deviations."""

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
        self.title = QLabel("BEHAVIORAL ANOMALIES & UNSUPERVISED OUTLIERS")
        self.subtitle = QLabel("Isolation Forest multivariate statistical outliers classified across behavioral deviation archetypes. Double-click row to view full entity dossier.")
        self.subtitle.setWordWrap(True)
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        layout.addLayout(title_box)

        # Filters Bar
        self.filter_bar = QFrame()
        fb_layout = QHBoxLayout(self.filter_bar)
        fb_layout.setContentsMargins(8, 6, 8, 6)
        fb_layout.setSpacing(12)

        fb_layout.addWidget(QLabel("Pattern:"))
        self.pattern_filter = ForensicComboBox()
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
        self.score_filter = ForensicComboBox()
        self.score_filter.addItems(["All Deviations (>= 0.0)", "Elevated (>= 0.50)", "High Outliers (>= 0.75)", "Severe (>= 0.85)"])
        self.score_filter.currentTextChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.score_filter)

        fb_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Entity ID...")
        self.search_input.textChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.search_input, 1)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self._reset_filters)
        fb_layout.addWidget(self.btn_reset)

        layout.addWidget(self.filter_bar)

        # Anomalies Table
        self.anomaly_table = QTableWidget(0, 8)
        self.anomaly_table.setHorizontalHeaderLabels([
            "Entity ID", "Anomaly Score", "Primary Archetype", "Fan-In / Fan-Out", "Relay IPs", "Countries", "Velocity", "Risk Score"
        ])
        header = self.anomaly_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)

        self.anomaly_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.anomaly_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.anomaly_table.setMinimumHeight(300)
        self.anomaly_table.doubleClicked.connect(self._open_entity_details)
        layout.addWidget(self.anomaly_table, 1)

        scroll.setWidget(content)
        page_layout.addWidget(scroll)

        self.entities: list[Entity] = []
        self.filtered_entities: list[Entity] = []

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
        # Filter entities with meaningful anomaly score
        self.entities = [e for e in pipeline.entities.values() if e.anomaly_score >= 0.20]
        self.entities.sort(key=lambda e: e.anomaly_score, reverse=True)
        self.filtered_entities = list(self.entities)
        self._populate_table(self.filtered_entities)

    def _populate_table(self, entities):
        self.anomaly_table.setRowCount(0)
        for i, e in enumerate(entities[:300]):
            self.anomaly_table.insertRow(i)
            item_id = QTableWidgetItem(e.entity_id)
            item_id.setToolTip(f"Double-click to open full forensic dossier for {e.entity_id}")
            self.anomaly_table.setItem(i, 0, item_id)
            self.anomaly_table.setItem(i, 1, QTableWidgetItem(f"{e.anomaly_score:.3f}"))

            # Determine dominant pattern
            pat = "Multivariate Deviation"
            reasons_str = " ".join(getattr(e, "reasons", [])).lower()
            if "burst" in reasons_str:
                pat = "Temporal Burst"
            elif "fan-out" in reasons_str or "fan_out" in reasons_str:
                pat = "High Fan-Out"
            elif "fan-in" in reasons_str or "fan_in" in reasons_str:
                pat = "High Fan-In"
            elif len(e.ips) > 2:
                pat = "Multi-IP Association"

            self.anomaly_table.setItem(i, 2, QTableWidgetItem(pat))
            fan_ratio = f"{getattr(e, 'in_degree', 0)} / {getattr(e, 'out_degree', 0)}"
            self.anomaly_table.setItem(i, 3, QTableWidgetItem(fan_ratio))
            self.anomaly_table.setItem(i, 4, QTableWidgetItem(str(len(e.ips))))
            self.anomaly_table.setItem(i, 5, QTableWidgetItem(str(e.unique_countries)))
            vel = f"{getattr(e, 'velocity', 0.0):.2f}/hr"
            self.anomaly_table.setItem(i, 6, QTableWidgetItem(vel))
            self.anomaly_table.setItem(i, 7, QTableWidgetItem(f"{e.risk_score:.1f}/100"))

    def _apply_filters(self):
        pat_choice = self.pattern_filter.currentText()
        score_choice = self.score_filter.currentText()
        q = self.search_input.text().strip().lower()

        min_score = 0.0
        if "0.50" in score_choice:
            min_score = 0.50
        elif "0.75" in score_choice:
            min_score = 0.75
        elif "0.85" in score_choice:
            min_score = 0.85

        filtered = [e for e in self.entities if e.anomaly_score >= min_score]
        if pat_choice != "All Behavioral Patterns":
            tag = pat_choice.lower()
            filtered = [
                e for e in filtered
                if any(tag in r.lower() for r in getattr(e, "reasons", []))
            ]

        if q:
            filtered = [e for e in filtered if q in e.entity_id.lower()]

        self.filtered_entities = filtered
        self._populate_table(self.filtered_entities)

    def _reset_filters(self):
        self.pattern_filter.setCurrentIndex(0)
        self.score_filter.setCurrentIndex(0)
        self.search_input.clear()
        self.filtered_entities = list(self.entities)
        self._populate_table(self.filtered_entities)

    def _open_entity_details(self, index):
        row = index.row()
        if 0 <= row < len(self.filtered_entities):
            ent = self.filtered_entities[row]
            dialog = EntityDetailsDialog(ent, parent=self)
            dialog.exec()
