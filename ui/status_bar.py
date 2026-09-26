"""Workstation bottom status bar."""
from PySide6.QtWidgets import QStatusBar, QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS


class StatusBar(QStatusBar):
    """Bottom status bar displaying environment safety and background task state."""

    def __init__(self):
        super().__init__()
        self.status_lbl = QLabel("Ready — System Idle")
        self.status_lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")
        self.addWidget(self.status_lbl, 1)

        self.net_lbl = QLabel("🔒 Outbound Network: Blocked")
        self.net_lbl.setStyleSheet(f"color: {THEME_COLORS['accent_emerald']}; font-size: 11px; font-weight: 600; margin-right: 16px;")
        self.addPermanentWidget(self.net_lbl)

        self.mem_lbl = QLabel("Analytical Buffer: OK")
        self.mem_lbl.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 11px; margin-right: 12px;")
        self.addPermanentWidget(self.mem_lbl)

    def set_status(self, message: str):
        self.status_lbl.setText(message)
