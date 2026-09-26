"""Reusable PySide6 custom widgets, KPI cards, and forensic badges."""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS


class KPICard(QFrame):
    """Forensic metric KPI card."""

    def __init__(self, title: str, value: str = "0", subtext: str = "", accent_color: str = "#38BDF8"):
        super().__init__()
        self.setObjectName("KPICard")
        self.setStyleSheet(f"""
            QFrame#KPICard {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border']};
                border-top: 3px solid {accent_color};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame#KPICard:hover {{
                border-color: {THEME_COLORS['border_light']};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        self.title_lbl = QLabel(title.upper())
        self.title_lbl.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")

        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 22px; font-weight: 700;")

        self.sub_lbl = QLabel(subtext)
        self.sub_lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.sub_lbl)

    def set_value(self, val: str, subtext: str = ""):
        self.val_lbl.setText(val)
        if subtext:
            self.sub_lbl.setText(subtext)


class RiskBadge(QLabel):
    """Semantic priority and risk indicator badge."""

    def __init__(self, text: str, level: str = "Low"):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.set_level(level)

    def set_level(self, level: str):
        colors_map = {
            "Critical": (THEME_COLORS["accent_red"], "rgba(239, 68, 68, 0.15)"),
            "High": (THEME_COLORS["accent_orange"], "rgba(249, 115, 22, 0.15)"),
            "Medium": (THEME_COLORS["accent_amber"], "rgba(245, 158, 11, 0.15)"),
            "Low": (THEME_COLORS["accent_emerald"], "rgba(16, 185, 129, 0.15)"),
            "Informational": (THEME_COLORS["accent_blue"], "rgba(56, 189, 248, 0.15)"),
        }
        fg, bg = colors_map.get(level, (THEME_COLORS["text_secondary"], THEME_COLORS["border"]))
        self.setStyleSheet(f"""
            QLabel {{
                color: {fg};
                background-color: {bg};
                border: 1px solid {fg};
                border-radius: 4px;
                padding: 3px 8px;
                font-weight: 700;
                font-size: 11px;
            }}
        """)


class EmptyStateWidget(QFrame):
    """Clean empty state displayed when no dataset is loaded."""

    def __init__(self, on_generate_demo=None, on_import_dataset=None):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        icon_lbl = QLabel("🛡️")
        icon_lbl.setStyleSheet("font-size: 48px;")
        icon_lbl.setAlignment(Qt.AlignCenter)

        title_lbl = QLabel("No Dataset Loaded")
        title_lbl.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        title_lbl.setAlignment(Qt.AlignCenter)

        desc_lbl = QLabel(
            "TRACE operates 100% offline on bulk Bitcoin transaction and P2P network metadata.\n"
            "Generate a synthetic demo dataset or import a local CSV, JSON, or XML file to begin analysis."
        )
        desc_lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 13px; text-align: center;")
        desc_lbl.setAlignment(Qt.AlignCenter)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)
        btn_box.setAlignment(Qt.AlignCenter)

        btn_demo = QPushButton("🚀 Generate Demo Dataset & Analyze")
        btn_demo.setObjectName("btn_demo")
        btn_demo.setProperty("class", "btn-primary")
        btn_demo.setStyleSheet(f"""
            QPushButton {{
                background-color: #2563EB;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 700;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #1D4ED8; }}
        """)
        if on_generate_demo:
            btn_demo.clicked.connect(on_generate_demo)

        btn_import = QPushButton("📂 Import Local File (CSV / JSON / XML)")
        btn_import.setProperty("class", "btn-secondary")
        btn_import.setStyleSheet(f"""
            QPushButton {{
                background-color: #1F2937;
                color: #F8FAFC;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #374151; }}
        """)
        if on_import_dataset:
            btn_import.clicked.connect(on_import_dataset)

        btn_box.addWidget(btn_demo)
        btn_box.addWidget(btn_import)

        layout.addStretch()
        layout.addWidget(icon_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)
        layout.addLayout(btn_box)
        layout.addStretch()
