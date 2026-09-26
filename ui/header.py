"""Workstation top header bar with status indicators and quick-action triggers."""
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PySide6.QtCore import Qt, Signal
from app.theme import THEME_COLORS


class Header(QFrame):
    """Top status and primary action header."""

    run_demo_requested = Signal()
    import_dataset_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("HeaderFrame")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)

        # Title & Context
        title_box = QHBoxLayout()
        title_box.setSpacing(8)

        self.title_lbl = QLabel("Bitcoin Traffic Forensic Console")
        self.title_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {THEME_COLORS['text_primary']};")

        self.dataset_tag = QLabel("[No Dataset Loaded]")
        self.dataset_tag.setStyleSheet(f"""
            background-color: {THEME_COLORS['bg_card']};
            border: 1px solid {THEME_COLORS['border_light']};
            color: {THEME_COLORS['text_muted']};
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: 600;
        """)

        title_box.addWidget(self.title_lbl)
        title_box.addWidget(self.dataset_tag)
        layout.addLayout(title_box)

        layout.addStretch()

        # Offline Verification Tag
        self.offline_tag = QLabel("🛡️ OFFLINE VERIFIED")
        self.offline_tag.setStyleSheet(f"""
            color: {THEME_COLORS['accent_emerald']};
            background-color: rgba(16, 185, 129, 0.1);
            border: 1px solid {THEME_COLORS['accent_emerald']};
            border-radius: 4px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 700;
        """)
        layout.addWidget(self.offline_tag)

        # Action Buttons
        self.btn_import = QPushButton("📂 Import Dataset")
        self.btn_import.setProperty("class", "btn-secondary")
        self.btn_import.setStyleSheet(f"""
            QPushButton {{
                background-color: #1F2937;
                color: #F8FAFC;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #374151; }}
        """)
        self.btn_import.clicked.connect(self.import_dataset_requested.emit)

        self.btn_demo = QPushButton("🚀 Run Demo Investigation")
        self.btn_demo.setProperty("class", "btn-primary")
        self.btn_demo.setStyleSheet(f"""
            QPushButton {{
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #1D4ED8; }}
        """)
        self.btn_demo.clicked.connect(self.run_demo_requested.emit)

        layout.addWidget(self.btn_import)
        layout.addWidget(self.btn_demo)

    def set_dataset_info(self, filename: str, record_count: int):
        self.dataset_tag.setText(f"📁 {filename} ({record_count} records)")
        self.dataset_tag.setStyleSheet(f"""
            background-color: rgba(56, 189, 248, 0.1);
            border: 1px solid {THEME_COLORS['accent_blue']};
            color: {THEME_COLORS['accent_blue']};
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: 600;
        """)
