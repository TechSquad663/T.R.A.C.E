"""Workstation sidebar navigation component."""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QPushButton, QLabel, QButtonGroup, QWidget, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from app.theme import THEME_COLORS, theme_manager


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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 16, 12, 14)
        main_layout.setSpacing(6)

        # Brand / Title
        self.brand_lbl = QLabel("TRACE")
        self.sub_brand_lbl = QLabel("SIH26146 • NTRO FORENSICS")

        main_layout.addWidget(self.brand_lbl)
        main_layout.addWidget(self.sub_brand_lbl)

        # Scrollable Nav Buttons Area
        self.nav_scroll = QScrollArea()
        self.nav_scroll.setWidgetResizable(True)
        self.nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        nav_widget = QWidget()
        nav_widget.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 4, 0, 4)
        nav_layout.setSpacing(4)

        # Nav button group
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.buttons = []

        for idx, (label, page_idx) in enumerate(self.NAV_ITEMS):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("class", "nav-btn")
            btn.setCursor(Qt.PointingHandCursor)
            if idx == 0:
                btn.setChecked(True)
            self.button_group.addButton(btn, page_idx)
            self.buttons.append(btn)
            nav_layout.addWidget(btn)

        self.button_group.idClicked.connect(self._on_button_clicked)
        nav_layout.addStretch()

        self.nav_scroll.setWidget(nav_widget)
        main_layout.addWidget(self.nav_scroll, 1)

        # Offline Verified Badge at bottom of sidebar
        self.offline_box = QFrame()
        off_layout = QVBoxLayout(self.offline_box)
        off_layout.setContentsMargins(8, 8, 8, 8)
        off_layout.setSpacing(2)

        self.off_title = QLabel("🔒 100% AIR-GAPPED")
        self.off_desc = QLabel("Outbound network disabled")

        off_layout.addWidget(self.off_title)
        off_layout.addWidget(self.off_desc)
        main_layout.addWidget(self.offline_box)

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update brand and offline badge styling with active theme colors."""
        self.brand_lbl.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 900;
            color: {THEME_COLORS['accent_blue']};
            letter-spacing: 2px;
            padding-left: 8px;
        """)

        self.sub_brand_lbl.setStyleSheet(f"""
            font-size: 9px;
            font-weight: 700;
            color: {THEME_COLORS['text_muted']};
            letter-spacing: 1px;
            padding-left: 8px;
            margin-bottom: 8px;
        """)

        self.offline_box.setStyleSheet(f"""
            background-color: rgba(16, 185, 129, 0.12);
            border: 1px solid {THEME_COLORS['accent_emerald']};
            border-radius: 6px;
            padding: 8px;
        """)

        self.off_title.setStyleSheet(f"color: {THEME_COLORS['accent_emerald']}; font-weight: 700; font-size: 11px;")
        self.off_desc.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 10px;")

    def _on_button_clicked(self, page_id: int):
        self.page_changed.emit(page_id)

    def set_active_page(self, page_id: int):
        for btn in self.buttons:
            if self.button_group.id(btn) == page_id:
                btn.setChecked(True)
                break
        # Emit so the QStackedWidget in main_window actually switches
        self.page_changed.emit(page_id)
