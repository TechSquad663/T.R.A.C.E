"""Entity intelligence explorer page with responsive filters and error-free selection."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
from core.models import Entity
from .entity_details import EntityDetailsDialog
from ui.components import ForensicComboBox, setup_table_headers


class EntityPage(QWidget):
    """Explorer for resolved Bitcoin entities and common-input clusters."""

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
        self.title = QLabel("ENTITY INTELLIGENCE & HEURISTIC CLUSTERING")
        self.subtitle = QLabel("Resolved entities grouped via Common Input Ownership (CIO) heuristic. Double-click row to view full dossier.")
        self.subtitle.setWordWrap(True)
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        layout.addLayout(title_box)

        # Filter & Search Bar
        self.filter_bar = QFrame()
        fb_layout = QHBoxLayout(self.filter_bar)
        fb_layout.setContentsMargins(8, 6, 8, 6)
        fb_layout.setSpacing(12)

        fb_layout.addWidget(QLabel("Priority:"))
        self.priority_combo = ForensicComboBox()
        self.priority_combo.addItems(["All Priorities", "Critical", "High", "Medium", "Low"])
        self.priority_combo.currentTextChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.priority_combo)

        fb_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Entity ID, wallet address, or associated IP...")
        self.search_input.textChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.search_input, 1)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self._reset_filters)
        fb_layout.addWidget(self.btn_reset)

        layout.addWidget(self.filter_bar)

        # Entity Table
        self.entity_table = QTableWidget(0, 8)
        setup_table_headers(self.entity_table)
        self.entity_table.setHorizontalHeaderLabels([
            "Priority", "Entity ID", "Type", "Risk Score", "Model Prob", "Anomaly Score", "Transactions", "Relay IPs"
        ])
        header = self.entity_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)

        self.entity_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.entity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.entity_table.setMinimumHeight(300)
        self.entity_table.doubleClicked.connect(self._open_entity_details)
        layout.addWidget(self.entity_table, 1)

        scroll.setWidget(content)
        page_layout.addWidget(scroll)

        self.entities: list[Entity] = []
        self.filtered_entities: list[Entity] = []

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update element styling according to active theme."""
        self.title.setStyleSheet(f"background: transparent; font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.subtitle.setStyleSheet(f"background: transparent; font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        self.filter_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border']};
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QLabel {{
                background: transparent;
            }}
        """)

    def update_data(self, pipeline):
        if not pipeline:
            return
        self.entities = list(pipeline.entities.values())
        self.entities.sort(key=lambda e: e.risk_score, reverse=True)
        self.filtered_entities = list(self.entities)
        self._populate_table(self.filtered_entities)

    def _populate_table(self, entities):
        self.entity_table.setRowCount(0)
        for i, e in enumerate(entities[:300]):
            self.entity_table.insertRow(i)
            self.entity_table.setItem(i, 0, QTableWidgetItem(e.priority.value))
            item_id = QTableWidgetItem(e.entity_id)
            item_id.setToolTip(f"Double-click to open full dossier for {e.entity_id}")
            self.entity_table.setItem(i, 1, item_id)
            self.entity_table.setItem(i, 2, QTableWidgetItem(e.entity_type.value))
            self.entity_table.setItem(i, 3, QTableWidgetItem(f"{e.risk_score:.1f}/100"))
            self.entity_table.setItem(i, 4, QTableWidgetItem(f"{e.model_probability:.2f}"))
            self.entity_table.setItem(i, 5, QTableWidgetItem(f"{e.anomaly_score:.2f}"))
            self.entity_table.setItem(i, 6, QTableWidgetItem(str(len(e.txids) or e.transaction_count)))
            self.entity_table.setItem(i, 7, QTableWidgetItem(str(len(e.ips))))

    def _apply_filters(self):
        q = self.search_input.text().strip().lower()
        prio = self.priority_combo.currentText()

        filtered = [
            e for e in self.entities
            if (prio == "All Priorities" or e.priority.value == prio)
            and (not q or q in e.entity_id.lower() or any(q in a.lower() for a in e.addresses) or any(q in ip.lower() for ip in e.ips))
        ]
        self.filtered_entities = filtered
        self._populate_table(self.filtered_entities)

    def _reset_filters(self):
        self.priority_combo.setCurrentIndex(0)
        self.search_input.clear()
        self.filtered_entities = list(self.entities)
        self._populate_table(self.filtered_entities)

    def _open_entity_details(self, index):
        row = index.row()
        if 0 <= row < len(self.filtered_entities):
            ent = self.filtered_entities[row]
            dialog = EntityDetailsDialog(ent, parent=self)
            dialog.exec()
