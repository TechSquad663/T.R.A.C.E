"""Entity intelligence deep-dive dialog with multi-layer evidentiary breakdown."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFrame, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS
from core.models import Entity
from ui.components import RiskBadge


class EntityDetailsDialog(QDialog):
    """Full forensic profile and evidentiary breakdown for a flagged entity."""

    def __init__(self, entity: Entity, docket: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Entity Intelligence Dossier — {entity.entity_id}")
        self.resize(800, 650)
        self.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; color: {THEME_COLORS['text_primary']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header Title
        title_box = QHBoxLayout()
        t_box = QVBoxLayout()
        t_lbl = QLabel(f"ENTITY PROFILE: {entity.entity_id}")
        t_lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        t_sub = QLabel(f"Type: {entity.entity_type.value} | Risk Indicator: {entity.risk_score}/100 | Confidence: {int(entity.confidence * 100)}%")
        t_sub.setStyleSheet(f"font-size: 12px; color: {THEME_COLORS['text_secondary']};")
        t_box.addWidget(t_lbl)
        t_box.addWidget(t_sub)
        title_box.addLayout(t_box)
        title_box.addStretch()

        badge = RiskBadge(entity.priority.value, entity.priority.value)
        title_box.addWidget(badge)
        layout.addLayout(title_box)

        # Metrics Card Grid
        grid_frame = QFrame()
        grid_frame.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 12px;")
        grid = QGridLayout(grid_frame)
        grid.setSpacing(8)

        grid.addWidget(QLabel("Supervised Model Prob:"), 0, 0)
        grid.addWidget(QLabel(f"<b>{entity.model_probability:.2f}</b>"), 0, 1)

        grid.addWidget(QLabel("Isolation Forest Anomaly:"), 0, 2)
        grid.addWidget(QLabel(f"<b>{entity.anomaly_score:.2f}</b>"), 0, 3)

        grid.addWidget(QLabel("Behavioral Cluster ID:"), 1, 0)
        grid.addWidget(QLabel(f"<b>Cohort #{entity.cluster_id}</b>"), 1, 1)

        grid.addWidget(QLabel("Observed Transactions:"), 1, 2)
        grid.addWidget(QLabel(f"<b>{entity.transaction_count}</b>"), 1, 3)

        grid.addWidget(QLabel("Flow Asymmetry:"), 2, 0)
        grid.addWidget(QLabel(f"<b>Fan-Out: {entity.fan_out_ratio:.2f} | Fan-In: {entity.fan_in_ratio:.2f}</b>"), 2, 1)

        grid.addWidget(QLabel("P2P Relay IP Count:"), 2, 2)
        grid.addWidget(QLabel(f"<b>{len(entity.ips)} endpoints</b>"), 2, 3)

        layout.addWidget(grid_frame)

        # "WHY FLAGGED" Section
        why_lbl = QLabel("WHY FLAGGED (MULTI-MODAL FORENSIC EVIDENCE)")
        why_lbl.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['accent_orange']}; margin-top: 4px;")
        layout.addWidget(why_lbl)

        reasons_box = QFrame()
        reasons_box.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 10px;")
        r_layout = QVBoxLayout(reasons_box)
        r_layout.setSpacing(4)
        for r in entity.reasons:
            lbl = QLabel(f"• {r}")
            lbl.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 11px;")
            r_layout.addWidget(lbl)
        layout.addWidget(reasons_box)

        # SHAP Top Feature Attributions
        shap_lbl = QLabel("TOP CONTRIBUTING BEHAVIORAL FEATURES (SHAP)")
        shap_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        layout.addWidget(shap_lbl)

        shap_txt = QTextEdit()
        shap_txt.setReadOnly(True)
        shap_lines = []
        for f in entity.top_contributing_features:
            fname = f.get("feature", "")
            impact = f.get("impact", 0.0)
            val = f.get("value", 0.0)
            desc = f.get("description", "")
            shap_lines.append(f"{fname:<24} | value: {val:<8.2f} | impact: {impact:+.4f} -> {desc}")
        shap_txt.setText("\n".join(shap_lines) if shap_lines else "Standard feature baseline")
        shap_txt.setFixedHeight(110)
        layout.addWidget(shap_txt)

        # Close
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border_light']}; color: {THEME_COLORS['text_primary']}; padding: 6px 16px; border-radius: 4px;")
        layout.addWidget(btn_close, alignment=Qt.AlignRight)
