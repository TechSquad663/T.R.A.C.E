"""Alert investigation view dialog with hierarchical forensic sections and scroll safety."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QFrame, QGridLayout, QScrollArea, QWidget, QApplication
)
from PySide6.QtCore import Qt, QTimer
from app.theme import THEME_COLORS, theme_manager
from core.models import Alert
from ui.components import RiskBadge


class AlertDetailsDialog(QDialog):
    """Detailed lead investigation dossier for an individual alert."""

    def __init__(self, alert: Alert, parent=None):
        super().__init__(parent)
        self.alert = alert
        self.setWindowTitle(f"Investigative Lead Dossier — {alert.alert_id}")
        self.resize(800, 620)
        self.setMinimumSize(620, 450)
        self.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; color: {THEME_COLORS['text_primary']};")

        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(16, 16, 16, 16)
        dialog_layout.setSpacing(10)

        # Header Title with Badge
        h_box = QHBoxLayout()
        title_box = QVBoxLayout()
        t_lbl = QLabel(f"INVESTIGATIVE LEAD DOSSIER: {alert.alert_id}")
        t_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        e_lbl = QLabel(f"Target Entity: {alert.entity_id}  |  Generated: {alert.timestamp[:19] if alert.timestamp else 'N/A'}")
        e_lbl.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        e_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_box.addWidget(t_lbl)
        title_box.addWidget(e_lbl)
        h_box.addLayout(title_box)
        h_box.addStretch()

        badge = RiskBadge(alert.priority.value, alert.priority.value)
        h_box.addWidget(badge)
        dialog_layout.addLayout(h_box)

        # Scroll Area for Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(12)

        # 1. Section: Risk Summary & Metric Matrix
        s1_lbl = QLabel("1. RISK & CONFIDENCE METRICS")
        s1_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        layout.addWidget(s1_lbl)

        grid_frame = QFrame()
        grid_frame.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 12px;")
        grid = QGridLayout(grid_frame)
        grid.setSpacing(10)

        grid.addWidget(QLabel("Fused Risk Indicator:"), 0, 0)
        grid.addWidget(QLabel(f"<b>{alert.risk_score:.1f} / 100</b>"), 0, 1)

        grid.addWidget(QLabel("Evidentiary Confidence:"), 0, 2)
        conf_pct = int(alert.confidence * 100) if alert.confidence else 0
        grid.addWidget(QLabel(f"<b>{conf_pct}% ({alert.evidence_strength.value})</b>"), 0, 3)

        grid.addWidget(QLabel("Primary Behavioral Archetype:"), 1, 0)
        grid.addWidget(QLabel(f"<b>{alert.pattern}</b>"), 1, 1)

        grid.addWidget(QLabel("Associated Relay Endpoints:"), 1, 2)
        grid.addWidget(QLabel(f"<b>{len(alert.related_ips)} unique IPs</b>"), 1, 3)

        grid.addWidget(QLabel("Correlated Transactions:"), 2, 0)
        grid.addWidget(QLabel(f"<b>{len(alert.related_transactions)} records</b>"), 2, 1)

        grid.addWidget(QLabel("Lead Priority Tier:"), 2, 2)
        grid.addWidget(QLabel(f"<b>{alert.priority.value}</b>"), 2, 3)

        layout.addWidget(grid_frame)

        # 2. Section: Why Flagged (Analytical Signals)
        s2_lbl = QLabel("2. WHY FLAGGED (EVIDENTIARY REASONS & DETECTIONS)")
        s2_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_orange']};")
        layout.addWidget(s2_lbl)

        r_box = QFrame()
        r_box.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 12px;")
        r_layout = QVBoxLayout(r_box)
        r_layout.setSpacing(6)
        if alert.reasons:
            for r in alert.reasons:
                lbl = QLabel(f"• {r}")
                lbl.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 11px;")
                lbl.setWordWrap(True)
                r_layout.addWidget(lbl)
        else:
            lbl = QLabel("• Statistical deviation detected across behavioral baseline.")
            lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")
            r_layout.addWidget(lbl)
        layout.addWidget(r_box)

        # 3. Section: Machine Learning Model Signals
        s3_lbl = QLabel("3. MACHINE LEARNING MODEL EXPLANATION")
        s3_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_purple']};")
        layout.addWidget(s3_lbl)

        ml_box = QFrame()
        ml_box.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 12px;")
        ml_layout = QGridLayout(ml_box)
        ml_layout.setSpacing(8)

        m_ev = alert.model_evidence or {}
        sup_prob = m_ev.get("model_probability", 0.0)
        ano_score = m_ev.get("anomaly_score", 0.0)

        ml_layout.addWidget(QLabel("Supervised XGBoost Probability:"), 0, 0)
        ml_layout.addWidget(QLabel(f"<b>{sup_prob:.4f}</b> (Threshold: 0.50)"), 0, 1)

        ml_layout.addWidget(QLabel("Isolation Forest Anomaly Score:"), 0, 2)
        ml_layout.addWidget(QLabel(f"<b>{ano_score:.4f}</b> (Multivariate outlier index)"), 0, 3)

        # Model decision factors if present
        factors = m_ev.get("top_factors", [])
        if factors:
            ml_layout.addWidget(QLabel("Influential Decision Signals:"), 1, 0)
            factors_str = ", ".join(factors)
            ml_layout.addWidget(QLabel(f"<b>{factors_str}</b>"), 1, 1, 1, 3)

        layout.addWidget(ml_box)

        # 4. Section: Related Network & Blockchain Artifacts
        s4_lbl = QLabel("4. CORRELATED TRANSACTION & RELAY ARTIFACTS")
        s4_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_emerald']};")
        layout.addWidget(s4_lbl)

        art_frame = QFrame()
        art_frame.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 10px;")
        art_layout = QVBoxLayout(art_frame)
        art_layout.setSpacing(6)

        tx_txt = QTextEdit()
        tx_txt.setReadOnly(True)
        tx_txt.setFixedHeight(75)
        tx_txt.setStyleSheet(f"background-color: {THEME_COLORS['bg_card_alt']}; border: 1px solid {THEME_COLORS['border']}; font-family: monospace; font-size: 11px; color: {THEME_COLORS['text_primary']};")
        tx_lines = [f"TXID: {tx}" for tx in alert.related_transactions]
        tx_txt.setText("\n".join(tx_lines) if tx_lines else "No specific TXIDs explicitly bound to this alert.")
        art_layout.addWidget(QLabel(f"Referenced Transactions ({len(alert.related_transactions)}):"))
        art_layout.addWidget(tx_txt)

        ips_str = ", ".join(alert.related_ips) if alert.related_ips else "No relay IPs recorded."
        ip_lbl = QLabel(f"Associated Relay Endpoints: <b>{ips_str}</b>")
        ip_lbl.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        ip_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        art_layout.addWidget(ip_lbl)

        layout.addWidget(art_frame)

        # Non-Accusatory Caveat
        c_frame = QFrame()
        c_frame.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border-left: 3px solid {THEME_COLORS['accent_amber']}; padding: 8px 12px; border-radius: 4px;")
        c_layout = QVBoxLayout(c_frame)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_lbl = QLabel(
            "COMPLIANCE & EVIDENTIARY DIRECTIVE: This alert represents an analytical triage lead generated from behavioral and graph metadata. "
            "It does not constitute conclusive evidence of illicit activity. Corroborate with external forensic sources before taking enforcement action."
        )
        c_lbl.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 10px; font-style: italic;")
        c_lbl.setWordWrap(True)
        c_layout.addWidget(c_lbl)
        layout.addWidget(c_frame)

        scroll.setWidget(content)
        dialog_layout.addWidget(scroll, 1)

        # Bottom Actions Bar
        act_box = QHBoxLayout()
        self.btn_copy_entity = QPushButton("📋 Copy Entity ID")
        self.btn_copy_entity.setCursor(Qt.PointingHandCursor)
        self.btn_copy_entity.clicked.connect(self._copy_entity_id)
        self.btn_copy_entity.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border_light']};
                color: {THEME_COLORS['text_primary']};
                padding: 6px 14px;
                border-radius: 4px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['bg_card_alt']};
            }}
        """)
        act_box.addWidget(self.btn_copy_entity)
        act_box.addStretch()

        btn_close = QPushButton("Close Dossier")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border_light']};
                color: {THEME_COLORS['text_primary']};
                padding: 6px 18px;
                border-radius: 4px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['bg_card_alt']};
                border-color: {THEME_COLORS['accent_blue']};
            }}
        """)
        act_box.addWidget(btn_close)
        dialog_layout.addLayout(act_box)

    def _copy_entity_id(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.alert.entity_id)
            self.btn_copy_entity.setText("✓ Copied Entity ID!")
            QTimer.singleShot(1800, lambda: self.btn_copy_entity.setText("📋 Copy Entity ID"))
