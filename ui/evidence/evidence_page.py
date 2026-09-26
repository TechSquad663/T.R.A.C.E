"""Forensic Evidence Chain page displaying end-to-end multi-layer causal traces."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTextEdit,
    QFrame, QScrollArea, QPushButton
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
from core.models import Alert
from core.constants import DISCLAIMER_TEXT


class EvidencePage(QWidget):
    """Forensic evidence station presenting structured multi-layer evidence chains."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Title
        title_box = QVBoxLayout()
        self.title = QLabel("STRUCTURED FORENSIC EVIDENCE CHAIN")
        self.subtitle = QLabel("Multi-layer evidentiary reconstruction linking network observations to blockchain settlement records.")
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        layout.addLayout(title_box)

        # Entity Selector Bar
        self.sel_bar = QFrame()
        sb_layout = QHBoxLayout(self.sel_bar)
        sb_layout.setContentsMargins(6, 4, 6, 4)
        sb_layout.setSpacing(12)

        sb_layout.addWidget(QLabel("Select Flagged Entity:"))
        self.entity_combo = QComboBox()
        self.entity_combo.setStyleSheet("min-width: 320px;")
        self.entity_combo.currentIndexChanged.connect(self._on_entity_selected)
        sb_layout.addWidget(self.entity_combo)
        sb_layout.addStretch()
        layout.addWidget(self.sel_bar)

        # Evidence Chain Scroll Container
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.chain_container = QWidget()
        self.chain_layout = QVBoxLayout(self.chain_container)
        self.chain_layout.setContentsMargins(4, 4, 4, 4)
        self.chain_layout.setSpacing(12)

        self.scroll_area.setWidget(self.chain_container)
        layout.addWidget(self.scroll_area)

        # Disclaimers at bottom
        self.disc_lbl = QLabel(DISCLAIMER_TEXT)
        self.disc_lbl.setWordWrap(True)
        layout.addWidget(self.disc_lbl)

        self.pipeline = None
        self.dockets = {}

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update element styling according to active theme."""
        self.title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        self.sel_bar.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 8px 12px;")
        self.disc_lbl.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 10px; font-style: italic; border-top: 1px solid {THEME_COLORS['border']}; padding-top: 8px;")
        # Re-render current docket with refreshed colors
        self._on_entity_selected(self.entity_combo.currentIndex())

    def update_data(self, pipeline):
        self.pipeline = pipeline
        if not pipeline or not pipeline.dockets:
            return
        self.dockets = pipeline.dockets
        self.entity_combo.clear()
        for ent_id in pipeline.entities.keys():
            self.entity_combo.addItem(ent_id)

    def _on_entity_selected(self, index=0):
        ent_id = self.entity_combo.currentText()
        if not ent_id or ent_id not in self.dockets:
            return
        docket = self.dockets[ent_id]
        self._render_docket(docket)

    def _render_docket(self, docket):
        # Clear existing chain widgets
        while self.chain_layout.count() > 0:
            item = self.chain_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        chain = docket.get("evidence_chain", [])
        if not chain:
            lbl = QLabel("No multi-hop path chain recorded for this entity.")
            lbl.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 13px; padding: 20px;")
            self.chain_layout.addWidget(lbl)
            return

        for step in chain:
            card = QFrame()
            card.setStyleSheet(f"""
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border']};
                border-left: 4px solid {THEME_COLORS['accent_blue']};
                border-radius: 6px;
                padding: 12px;
            """)
            c_layout = QVBoxLayout(card)
            c_layout.setSpacing(6)

            # Step title
            step_header = QHBoxLayout()
            h_lbl = QLabel(f"STEP {step.get('step_number', 1)}: {step.get('layer', '')}")
            h_lbl.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
            step_header.addWidget(h_lbl)
            step_header.addStretch()

            conf = int(step.get("confidence", 0.9) * 100)
            c_badge = QLabel(f"Confidence: {conf}%")
            c_badge.setStyleSheet(f"color: {THEME_COLORS['accent_emerald']}; font-weight: 700; font-size: 11px;")
            step_header.addWidget(c_badge)
            c_layout.addLayout(step_header)

            # Description & Links
            path_desc = QLabel(f"<b>{step.get('source')}</b>  --[{step.get('relationship')}]-->  <b>{step.get('target')}</b>")
            path_desc.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 13px; font-family: monospace;")
            c_layout.addWidget(path_desc)

            supp = QLabel(f"Supporting Forensic Record: {step.get('supporting_record', '')}")
            supp.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")
            c_layout.addWidget(supp)

            caveat = QLabel(f"Evidentiary Note: {step.get('caveat', '')}")
            caveat.setStyleSheet(f"color: {THEME_COLORS['accent_amber']}; font-size: 10px; font-style: italic;")
            c_layout.addWidget(caveat)

            self.chain_layout.addWidget(card)

        self.chain_layout.addStretch()
