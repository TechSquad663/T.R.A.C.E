"""Forensic Evidence Chain page displaying end-to-end multi-layer causal traces with stepper visualization."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QPushButton
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
from core.constants import DISCLAIMER_TEXT
from ui.components import ForensicComboBox


class EvidencePage(QWidget):
    """Forensic evidence station presenting structured multi-layer evidence chains."""

    def __init__(self):
        super().__init__()
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)

        # Outer page scroll so header/selector never get clipped on small screens
        outer_scroll = QScrollArea()
        outer_scroll.setWidgetResizable(True)
        outer_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        outer_content = QWidget()
        layout = QVBoxLayout(outer_content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Title
        title_box = QVBoxLayout()
        self.title = QLabel("STRUCTURED FORENSIC EVIDENCE CHAIN")
        self.subtitle = QLabel("Multi-layer evidentiary reconstruction linking network observations to blockchain settlement records.")
        self.subtitle.setWordWrap(True)
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        layout.addLayout(title_box)

        # Entity Selector Bar
        self.sel_bar = QFrame()
        sb_layout = QHBoxLayout(self.sel_bar)
        sb_layout.setContentsMargins(8, 6, 8, 6)
        sb_layout.setSpacing(12)

        sb_layout.addWidget(QLabel("Select Flagged Entity:"))
        self.entity_combo = ForensicComboBox()
        self.entity_combo.setMinimumWidth(320)
        self.entity_combo.currentIndexChanged.connect(self._on_entity_selected)
        sb_layout.addWidget(self.entity_combo)
        sb_layout.addStretch()
        layout.addWidget(self.sel_bar)

        # Evidence Chain Scroll Container — inner scroll for the chain cards
        self.chain_scroll = QScrollArea()
        self.chain_scroll.setWidgetResizable(True)
        self.chain_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.chain_scroll.setMinimumHeight(300)

        self.chain_container = QWidget()
        self.chain_layout = QVBoxLayout(self.chain_container)
        self.chain_layout.setContentsMargins(4, 4, 4, 4)
        self.chain_layout.setSpacing(8)

        self.chain_scroll.setWidget(self.chain_container)
        layout.addWidget(self.chain_scroll, 1)

        # Disclaimer at bottom
        self.disc_lbl = QLabel(DISCLAIMER_TEXT)
        self.disc_lbl.setWordWrap(True)
        layout.addWidget(self.disc_lbl)

        outer_scroll.setWidget(outer_content)
        page_layout.addWidget(outer_scroll)

        self.pipeline = None
        self.dockets = {}

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

        # Initial empty state
        self._render_empty_state()

    def refresh_theme(self):
        """Update element styling according to active theme."""
        self.title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        self.sel_bar.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 6px 12px;")
        self.disc_lbl.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 10px; font-style: italic; border-top: 1px solid {THEME_COLORS['border']}; padding-top: 8px;")

        # Re-render current docket with refreshed colors
        if self.entity_combo.count() > 0:
            self._on_entity_selected(self.entity_combo.currentIndex())
        else:
            self._render_empty_state()

    def _render_empty_state(self):
        while self.chain_layout.count() > 0:
            item = self.chain_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        empty_frame = QFrame()
        empty_frame.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px dashed {THEME_COLORS['border']}; border-radius: 8px; padding: 30px;")
        ef_layout = QVBoxLayout(empty_frame)
        ef_layout.setAlignment(Qt.AlignCenter)
        ef_layout.setSpacing(10)

        icon = QLabel("🔗")
        icon.setStyleSheet("font-size: 36px;")
        icon.setAlignment(Qt.AlignCenter)
        ef_layout.addWidget(icon)

        t_lbl = QLabel("No Evidence Dockets Available")
        t_lbl.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 15px; font-weight: 700;")
        t_lbl.setAlignment(Qt.AlignCenter)
        ef_layout.addWidget(t_lbl)

        d_lbl = QLabel("Ingest a dataset from the Dataset Ingestion tab or launch the one-click demo from Command Center to reconstruct multi-layer forensic evidence chains.")
        d_lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")
        d_lbl.setWordWrap(True)
        d_lbl.setAlignment(Qt.AlignCenter)
        ef_layout.addWidget(d_lbl)

        self.chain_layout.addWidget(empty_frame)
        self.chain_layout.addStretch()

    def update_data(self, pipeline):
        self.pipeline = pipeline
        if not pipeline or not pipeline.dockets:
            self._render_empty_state()
            return
        self.dockets = pipeline.dockets
        self.entity_combo.blockSignals(True)
        self.entity_combo.clear()
        for ent_id in pipeline.entities.keys():
            self.entity_combo.addItem(ent_id)
        self.entity_combo.blockSignals(False)

        if self.entity_combo.count() > 0:
            self._on_entity_selected(0)

    def _on_entity_selected(self, index=0):
        ent_id = self.entity_combo.currentText()
        if not ent_id or ent_id not in self.dockets:
            self._render_empty_state()
            return
        docket = self.dockets[ent_id]
        self._render_docket(docket)

    STEP_ICONS = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]

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

        for idx, step in enumerate(chain):
            step_num = step.get('step_number', idx + 1)
            icon = self.STEP_ICONS[min(step_num - 1, len(self.STEP_ICONS) - 1)]

            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {THEME_COLORS['bg_card']};
                    border: 1px solid {THEME_COLORS['border']};
                    border-left: 4px solid {THEME_COLORS['accent_blue']};
                    border-radius: 6px;
                    padding: 10px 14px;
                }}
                QFrame:hover {{
                    border-color: {THEME_COLORS['border_light']};
                }}
            """)
            c_layout = QVBoxLayout(card)
            c_layout.setSpacing(6)

            # Step title
            step_header = QHBoxLayout()
            h_lbl = QLabel(f"{icon} STEP {step_num}: {step.get('layer', '').upper()}")
            h_lbl.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
            step_header.addWidget(h_lbl)
            step_header.addStretch()

            conf = int(step.get("confidence", 0.9) * 100)
            c_badge = QLabel(f"Evidentiary Weight: {conf}%")
            c_badge.setStyleSheet(f"color: {THEME_COLORS['accent_emerald']}; font-weight: 700; font-size: 11px;")
            step_header.addWidget(c_badge)
            c_layout.addLayout(step_header)

            # Description & Links
            path_desc = QLabel(f"<b>{step.get('source')}</b>  ──[{step.get('relationship')}]──▶  <b>{step.get('target')}</b>")
            path_desc.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 12px; font-family: monospace;")
            path_desc.setTextInteractionFlags(Qt.TextSelectableByMouse)
            path_desc.setWordWrap(True)
            c_layout.addWidget(path_desc)

            supp = QLabel(f"Supporting Forensic Record: {step.get('supporting_record', '')}")
            supp.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")
            c_layout.addWidget(supp)

            caveat = QLabel(f"Forensic Context: {step.get('caveat', '')}")
            caveat.setStyleSheet(f"color: {THEME_COLORS['accent_amber']}; font-size: 10px; font-style: italic;")
            caveat.setWordWrap(True)
            c_layout.addWidget(caveat)

            self.chain_layout.addWidget(card)

            # Stepper connector arrow (except for the last card)
            if idx < len(chain) - 1:
                arrow_lbl = QLabel("▼")
                arrow_lbl.setAlignment(Qt.AlignCenter)
                arrow_lbl.setStyleSheet(f"color: {THEME_COLORS['accent_blue']}; font-size: 12px; padding: 2px 0;")
                self.chain_layout.addWidget(arrow_lbl)

        self.chain_layout.addStretch()
