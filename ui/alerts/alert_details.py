"""Alert investigation view dialog."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS
from core.models import Alert
from ui.components import RiskBadge


class AlertDetailsDialog(QDialog):
    """Detailed lead investigation dossier for an individual alert."""

    def __init__(self, alert: Alert, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Investigative Lead Dossier — {alert.alert_id}")
        self.resize(750, 580)
        self.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; color: {THEME_COLORS['text_primary']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header Title
        h_box = QHBoxLayout()
        title_box = QVBoxLayout()
        t_lbl = QLabel(f"INVESTIGATIVE LEAD: {alert.alert_id}")
        t_lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        e_lbl = QLabel(f"Subject Entity: {alert.entity_id} | Timestamp: {alert.timestamp[:19]}")
        e_lbl.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        title_box.addWidget(t_lbl)
        title_box.addWidget(e_lbl)
        h_box.addLayout(title_box)
        h_box.addStretch()

        badge = RiskBadge(alert.priority.value, alert.priority.value)
        h_box.addWidget(badge)
        layout.addLayout(h_box)

        # Grid Summary
        grid_frame = QFrame()
        grid_frame.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 12px;")
        grid = QGridLayout(grid_frame)
        grid.setSpacing(8)

        grid.addWidget(QLabel("Risk Indicator:"), 0, 0)
        grid.addWidget(QLabel(f"<b>{alert.risk_score}/100</b>"), 0, 1)

        grid.addWidget(QLabel("Evidentiary Confidence:"), 0, 2)
        grid.addWidget(QLabel(f"<b>{int(alert.confidence * 100)}% ({alert.evidence_strength.value})</b>"), 0, 3)

        grid.addWidget(QLabel("Supervised Model Prob:"), 1, 0)
        grid.addWidget(QLabel(f"<b>{alert.model_evidence.get('model_probability', 0.0):.2f}</b>"), 1, 1)

        grid.addWidget(QLabel("Anomaly Score:"), 1, 2)
        grid.addWidget(QLabel(f"<b>{alert.model_evidence.get('anomaly_score', 0.0):.2f}</b>"), 1, 3)

        grid.addWidget(QLabel("Primary Pattern:"), 2, 0)
        grid.addWidget(QLabel(f"<b>{alert.pattern}</b>"), 2, 1)

        grid.addWidget(QLabel("Associated Relay IPs:"), 2, 2)
        grid.addWidget(QLabel(f"<b>{len(alert.related_ips)} endpoints</b>"), 2, 3)

        layout.addWidget(grid_frame)

        # Reasons
        r_lbl = QLabel("ANALYTICAL JUSTIFICATION & SIGNALS")
        r_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_orange']};")
        layout.addWidget(r_lbl)

        r_box = QFrame()
        r_box.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 10px;")
        r_layout = QVBoxLayout(r_box)
        r_layout.setSpacing(4)
        for r in alert.reasons:
            lbl = QLabel(f"• {r}")
            lbl.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 11px;")
            r_layout.addWidget(lbl)
        layout.addWidget(r_box)

        # Non-Accusatory Caveat
        c_lbl = QLabel(
            "COMPLIANCE NOTICE: This alert represents an analytical triage lead generated from behavioral metadata. "
            "It does not constitute independent proof of criminality. Corroborate with external forensic sources."
        )
        c_lbl.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 10px; font-style: italic;")
        c_lbl.setWordWrap(True)
        layout.addWidget(c_lbl)

        # Close button
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border_light']}; color: {THEME_COLORS['text_primary']}; padding: 6px 16px; border-radius: 4px;")
        layout.addWidget(btn_close, alignment=Qt.AlignRight)
