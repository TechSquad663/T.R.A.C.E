from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QComboBox, QListView
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager


class ForensicComboBox(QComboBox):
    """Clean QComboBox with dedicated QListView popup to prevent Windows rendering artifacts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setView(QListView(self))



class KPICard(QFrame):
    """Forensic metric KPI card."""

    def __init__(self, title: str, value: str = "0", subtext: str = "", accent_color: str = "#38BDF8"):
        super().__init__()
        self.setObjectName("KPICard")
        self.title_text = title
        self.subtext = subtext
        self.accent_color = accent_color

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        self.title_lbl = QLabel(title.upper())
        self.val_lbl = QLabel(value)
        self.sub_lbl = QLabel(subtext)

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.sub_lbl)

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Reapply dynamic colors based on active theme."""
        self.setStyleSheet(f"""
            QFrame#KPICard {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border']};
                border-top: 3px solid {self.accent_color};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame#KPICard:hover {{
                border-color: {THEME_COLORS['border_light']};
            }}
        """)
        self.title_lbl.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")
        self.val_lbl.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 22px; font-weight: 700;")
        self.sub_lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")

    def set_value(self, val: str, subtext: str = ""):
        self.val_lbl.setText(val)
        if subtext:
            self.sub_lbl.setText(subtext)


class RiskBadge(QLabel):
    """Semantic priority and risk indicator badge."""

    def __init__(self, text: str, level: str = "Low"):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.level = level
        self.set_level(level)
        theme_manager.theme_changed.connect(lambda _: self.set_level(self.level))

    def set_level(self, level: str):
        self.level = level
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

        self.title_lbl = QLabel("No Dataset Loaded")
        self.title_lbl.setAlignment(Qt.AlignCenter)

        self.desc_lbl = QLabel(
            "TRACE operates 100% offline on bulk Bitcoin transaction and P2P network metadata.\n"
            "Generate a synthetic demo dataset or import a local CSV, JSON, or XML file to begin analysis."
        )
        self.desc_lbl.setAlignment(Qt.AlignCenter)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)
        btn_box.setAlignment(Qt.AlignCenter)

        self.btn_demo = QPushButton("🚀 Generate Demo Dataset & Analyze")
        self.btn_demo.setObjectName("btn_demo")
        self.btn_demo.setProperty("class", "btn-primary")
        if on_generate_demo:
            self.btn_demo.clicked.connect(on_generate_demo)

        self.btn_import = QPushButton("📂 Import Local File (CSV / JSON / XML)")
        self.btn_import.setProperty("class", "btn-secondary")
        if on_import_dataset:
            self.btn_import.clicked.connect(on_import_dataset)

        btn_box.addWidget(self.btn_demo)
        btn_box.addWidget(self.btn_import)

        layout.addWidget(icon_lbl)
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.desc_lbl)
        layout.addLayout(btn_box)

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update text and button styles according to current theme."""
        self.title_lbl.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        self.desc_lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 13px; text-align: center;")
        self.btn_demo.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['accent_blue']};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 700;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #1D4ED8; }}
        """)
        self.btn_import.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['bg_card']};
                color: {THEME_COLORS['text_primary']};
                border: 1px solid {THEME_COLORS['border_light']};
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {THEME_COLORS['bg_card_alt']}; border-color: {THEME_COLORS['accent_blue']}; }}
        """)
