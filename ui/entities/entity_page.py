"""Entity intelligence explorer page."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS
from core.models import Entity
from .entity_details import EntityDetailsDialog


class EntityPage(QWidget):
    """Explorer for resolved Bitcoin entities and common-input clusters."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Title
        title_box = QVBoxLayout()
        title = QLabel("ENTITY INTELLIGENCE & HEURISTIC CLUSTERING")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        subtitle = QLabel("Resolved entities grouped via Common Input Ownership (CIO) heuristic with behavioral profiles.")
        subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Entity ID, wallet address, or associated IP...")
        self.search_input.textChanged.connect(self._filter_entities)
        layout.addWidget(self.search_input)

        # Entity Table
        self.entity_table = QTableWidget(0, 8)
        self.entity_table.setHorizontalHeaderLabels([
            "Priority", "Entity ID", "Type", "Risk Score", "Model Prob", "Anomaly Score", "Transactions", "Relay IPs"
        ])
        self.entity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.entity_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.entity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.entity_table.doubleClicked.connect(self._open_entity_details)
        layout.addWidget(self.entity_table)

        self.entities: list[Entity] = []

    def update_data(self, pipeline):
        if not pipeline:
            return
        self.entities = list(pipeline.entities.values())
        # Sort by risk score descending
        self.entities.sort(key=lambda e: e.risk_score, reverse=True)
        self._populate_table(self.entities)

    def _populate_table(self, entities):
        self.entity_table.setRowCount(0)
        for i, e in enumerate(entities[:300]):
            self.entity_table.insertRow(i)
            self.entity_table.setItem(i, 0, QTableWidgetItem(e.priority.value))
            self.entity_table.setItem(i, 1, QTableWidgetItem(e.entity_id))
            self.entity_table.setItem(i, 2, QTableWidgetItem(e.entity_type.value))
            self.entity_table.setItem(i, 3, QTableWidgetItem(f"{e.risk_score}/100"))
            self.entity_table.setItem(i, 4, QTableWidgetItem(f"{e.model_probability:.2f}"))
            self.entity_table.setItem(i, 5, QTableWidgetItem(f"{e.anomaly_score:.2f}"))
            self.entity_table.setItem(i, 6, QTableWidgetItem(str(e.transaction_count)))
            self.entity_table.setItem(i, 7, QTableWidgetItem(str(len(e.ips))))

    def _filter_entities(self, query: str):
        q = query.strip().lower()
        if not q:
            self._populate_table(self.entities)
            return

        filtered = [
            e for e in self.entities
            if q in e.entity_id.lower() or any(q in a.lower() for a in e.addresses) or any(q in ip.lower() for ip in e.ips)
        ]
        self._populate_table(filtered)

    def _open_entity_details(self, index):
        row = index.row()
        if row < len(self.entities):
            ent = self.entities[row]
            dialog = EntityDetailsDialog(ent, parent=self)
            dialog.exec()
