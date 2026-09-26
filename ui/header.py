"""Workstation top header bar with status indicators, theme switcher, and quick-action triggers."""
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PySide6.QtCore import Qt, Signal
from app.theme import THEME_COLORS, theme_manager


class Header(QFrame):
    """Top status and primary action header."""

    run_demo_requested = Signal()
    import_dataset_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("HeaderFrame")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(14)

        # Title & Context
        title_box = QHBoxLayout()
        title_box.setSpacing(8)

        self.title_lbl = QLabel("Bitcoin Traffic Forensic Console")
        self.dataset_tag = QLabel("[No Dataset Loaded]")
        self.current_dataset_name = None
        self.current_record_count = 0

        title_box.addWidget(self.title_lbl)
        title_box.addWidget(self.dataset_tag)
        layout.addLayout(title_box)

        layout.addStretch()

        # Offline Verification Tag
        self.offline_tag = QLabel("🛡️ OFFLINE VERIFIED")
        layout.addWidget(self.offline_tag)

        # Theme Switcher Button
        self.btn_theme = QPushButton("☀️ Light Mode")
        self.btn_theme.setCursor(Qt.PointingHandCursor)
        self.btn_theme.setToolTip("Toggle between Dark Workstation and Light Analyst theme")
        self.btn_theme.clicked.connect(self._toggle_theme)
        layout.addWidget(self.btn_theme)

        # Action Buttons
        self.btn_import = QPushButton("📂 Import Dataset")
        self.btn_import.setProperty("class", "btn-secondary")
        self.btn_import.clicked.connect(self.import_dataset_requested.emit)

        self.btn_demo = QPushButton("🚀 Run Demo Investigation")
        self.btn_demo.setProperty("class", "btn-primary")
        self.btn_demo.clicked.connect(self.run_demo_requested.emit)

        layout.addWidget(self.btn_import)
        layout.addWidget(self.btn_demo)

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def _toggle_theme(self):
        theme_manager.toggle_theme()

    def refresh_theme(self):
        """Update header components styling according to active theme."""
        is_dark = theme_manager.is_dark()
        self.title_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {THEME_COLORS['text_primary']};")

        # Dataset tag styling
        if self.current_dataset_name:
            self.dataset_tag.setStyleSheet(f"""
                background-color: rgba(56, 189, 248, 0.12);
                border: 1px solid {THEME_COLORS['accent_blue']};
                color: {THEME_COLORS['accent_blue']};
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
            """)
        else:
            self.dataset_tag.setStyleSheet(f"""
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border_light']};
                color: {THEME_COLORS['text_muted']};
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
            """)

        # Offline tag styling
        self.offline_tag.setStyleSheet(f"""
            color: {THEME_COLORS['accent_emerald']};
            background-color: rgba(16, 185, 129, 0.12);
            border: 1px solid {THEME_COLORS['accent_emerald']};
            border-radius: 4px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 700;
        """)

        # Theme toggle button styling & text
        if is_dark:
            self.btn_theme.setText("☀️ Light Mode")
            self.btn_theme.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1E293B;
                    color: #F8FAFC;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    padding: 5px 12px;
                    font-weight: 600;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: #334155;
                    border-color: {THEME_COLORS['accent_blue']};
                }}
            """)
        else:
            self.btn_theme.setText("🌙 Dark Mode")
            self.btn_theme.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    color: #0F172A;
                    border: 1px solid #CBD5E1;
                    border-radius: 6px;
                    padding: 5px 12px;
                    font-weight: 600;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: #F1F5F9;
                    border-color: {THEME_COLORS['accent_blue']};
                }}
            """)

        # Import & Demo button styling
        self.btn_import.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['bg_card']};
                color: {THEME_COLORS['text_primary']};
                border: 1px solid {THEME_COLORS['border_light']};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['bg_card_alt']};
                border-color: {THEME_COLORS['accent_blue']};
            }}
        """)

        self.btn_demo.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['accent_blue']};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {"#1D4ED8" if is_dark else "#0369A1"};
            }}
        """)

    def set_dataset_info(self, filename: str, record_count: int):
        self.current_dataset_name = filename
        self.current_record_count = record_count
        self.dataset_tag.setText(f"📁 {filename} ({record_count} records)")
        self.dataset_tag.setStyleSheet(f"""
            background-color: rgba(56, 189, 248, 0.12);
            border: 1px solid {THEME_COLORS['accent_blue']};
            color: {THEME_COLORS['accent_blue']};
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: 600;
        """)
