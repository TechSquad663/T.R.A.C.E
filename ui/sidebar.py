"""Workstation sidebar navigation component."""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QPushButton, QLabel, QButtonGroup, QWidget
)
from PySide6.QtCore import Qt, Signal
from app.theme import THEME_COLORS


class Sidebar(QFrame):
    """Forensic workstation primary navigation sidebar."""

    page_changed = Signal(int)

    NAV_ITEMS = [
        ("📊 Overview", 0),
        ("📥 Dataset Ingestion", 1),
        ("⛓️ Transactions", 2),
        ("👛 Entities & Wallets", 3),
        ("🕸️ Link Analysis", 4),
        ("⚡ Behavioral Anomalies", 5),
        ("🚨 Ranked Alerts", 6),
        ("📁 Investigations", 7),
        ("🔍 Evidence Chain", 8),
        ("📈 Model Evaluation", 9),
        ("📄 Reports & Exports", 10),
        ("⚙️ System & Settings", 11),
    ]

    def __init__(self):
        super().__init__()
        self.setObjectName("SidebarFrame")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # Brand / Title
        brand_lbl = QLabel("TRACE")
        brand_lbl.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 900;
            color: {THEME_COLORS['accent_blue']};
            letter-spacing: 2px;
            padding-left: 8px;
        """)

        sub_brand_lbl = QLabel("SIH26146 • NTRO FORENSICS")
        sub_brand_lbl.setStyleSheet(f"""
            font-size: 9px;
            font-weight: 700;
            color: {THEME_COLORS['text_muted']};
            letter-spacing: 1px;
            padding-left: 8px;
            margin-bottom: 12px;
        """)

        layout.addWidget(brand_lbl)
        layout.addWidget(sub_brand_lbl)

        # Nav button group
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.buttons = []

        for idx, (label, page_idx) in enumerate(self.NAV_ITEMS):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("class", "nav-btn")
            if idx == 0:
                btn.setChecked(True)
            self.button_group.addButton(btn, page_idx)
            self.buttons.append(btn)
            layout.addWidget(btn)

        self.button_group.idClicked.connect(self._on_button_clicked)

        layout.addStretch()

        # Offline Verified Badge at bottom of sidebar
        offline_box = QFrame()
        offline_box.setStyleSheet(f"""
            background-color: rgba(16, 185, 129, 0.1);
            border: 1px solid {THEME_COLORS['accent_emerald']};
            border-radius: 6px;
            padding: 8px;
        """)
        off_layout = QVBoxLayout(offline_box)
        off_layout.setContentsMargins(6, 6, 6, 6)
        off_layout.setSpacing(2)

        off_title = QLabel("🔒 100% AIR-GAPPED")
        off_title.setStyleSheet(f"color: {THEME_COLORS['accent_emerald']}; font-weight: 700; font-size: 11px;")
        off_desc = QLabel("Outbound network disabled")
        off_desc.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 10px;")

        off_layout.addWidget(off_title)
        off_layout.addWidget(off_desc)
        layout.addWidget(offline_box)

    def _on_button_clicked(self, page_id: int):
        self.page_changed.emit(page_id)

    def set_active_page(self, page_id: int):
        btn = self.button_group.button(page_id)
        if btn:
            btn.setChecked(True)
