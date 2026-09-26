"""Reports and Exports page."""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QFrame, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
from config.settings import get_settings
from reports.pdf_report import ForensicPDFReportGenerator
from reports.csv_export import export_alerts_to_csv, export_entities_to_csv
from reports.json_export import export_docket_to_json


class ReportsPage(QWidget):
    """Forensic report generation and investigative export console."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header Title
        title_box = QVBoxLayout()
        self.title = QLabel("FORENSIC REPORT GENERATION & DATA EXPORTS")
        self.subtitle = QLabel("Generate audit-ready 12-section PDF lead reports, evidence dossiers, and tabular CSV extracts.")
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        layout.addLayout(title_box)

        # PDF Report Section Card
        self.pdf_card = QFrame()
        pc_layout = QVBoxLayout(self.pdf_card)
        pc_layout.setSpacing(12)

        self.pc_title = QLabel("📄 TRACE INVESTIGATIVE LEAD REPORT (PDF)")
        pc_layout.addWidget(self.pc_title)

        self.pc_desc = QLabel(
            "Compiles a comprehensive 12-section offline PDF dossier including executive summary, "
            "risk fusion indicators, SHAP attributions, network relay endpoints, multi-hop evidence chains, "
            "and statutory disclaimers."
        )
        pc_layout.addWidget(self.pc_desc)

        ent_select_box = QHBoxLayout()
        ent_select_box.addWidget(QLabel("Select Target Lead:"))
        self.entity_combo = QComboBox()
        self.entity_combo.setStyleSheet("min-width: 280px;")
        ent_select_box.addWidget(self.entity_combo)
        ent_select_box.addStretch()

        self.btn_gen_pdf = QPushButton("📑 Generate Official PDF Lead Report")
        self.btn_gen_pdf.clicked.connect(self._generate_pdf)
        ent_select_box.addWidget(self.btn_gen_pdf)

        pc_layout.addLayout(ent_select_box)
        layout.addWidget(self.pdf_card)

        # Tabular Data Exports Card
        self.exp_card = QFrame()
        ec_layout = QVBoxLayout(self.exp_card)
        ec_layout.setSpacing(12)

        self.ec_title = QLabel("📊 TABULAR & EVIDENCE EXPORTS (CSV / JSON)")
        ec_layout.addWidget(self.ec_title)

        self.ec_desc = QLabel("Export structured alerts, resolved entities, and raw evidence dockets for external offline analytical tools.")
        ec_layout.addWidget(self.ec_desc)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_exp_alerts = QPushButton("📥 Export Alerts (CSV)")
        self.btn_exp_alerts.clicked.connect(self._export_alerts_csv)
        btn_row.addWidget(self.btn_exp_alerts)

        self.btn_exp_entities = QPushButton("📥 Export Entities (CSV)")
        self.btn_exp_entities.clicked.connect(self._export_entities_csv)
        btn_row.addWidget(self.btn_exp_entities)

        self.btn_exp_json = QPushButton("📥 Export Evidence Docket (JSON)")
        self.btn_exp_json.clicked.connect(self._export_docket_json)
        btn_row.addWidget(self.btn_exp_json)

        btn_row.addStretch()
        ec_layout.addLayout(btn_row)
        layout.addWidget(self.exp_card)

        layout.addStretch()

        self.pipeline = None

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update element styling according to active theme."""
        is_dark = theme_manager.is_dark()
        self.title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")

        self.pdf_card.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 8px; padding: 16px;")
        self.pc_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        self.pc_desc.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px;")

        self.btn_gen_pdf.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['accent_blue']};
                color: white;
                padding: 8px 18px;
                border: none;
                border-radius: 6px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {"#1D4ED8" if is_dark else "#0369A1"};
            }}
        """)

        self.exp_card.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 8px; padding: 16px;")
        self.ec_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {THEME_COLORS['accent_emerald']};")
        self.ec_desc.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px;")

        btn_style = f"""
            QPushButton {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border_light']};
                color: {THEME_COLORS['text_primary']};
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['bg_card_alt']};
                border-color: {THEME_COLORS['accent_blue']};
            }}
        """
        self.btn_exp_alerts.setStyleSheet(btn_style)
        self.btn_exp_entities.setStyleSheet(btn_style)
        self.btn_exp_json.setStyleSheet(btn_style)

    def update_data(self, pipeline):
        self.pipeline = pipeline
        if not pipeline or not pipeline.dockets:
            return
        self.entity_combo.clear()
        for ent_id in pipeline.entities.keys():
            self.entity_combo.addItem(ent_id)

    def _generate_pdf(self):
        ent_id = self.entity_combo.currentText()
        if not ent_id or not self.pipeline or ent_id not in self.pipeline.dockets:
            QMessageBox.warning(self, "No Target", "Please select a target investigative lead from an active dataset.")
            return

        settings = get_settings()
        out_dir = settings.EXPORTS_DIR
        out_path = out_dir / f"Lead_Report_{ent_id}.pdf"

        docket = self.pipeline.dockets[ent_id]
        meta = {
            "entity_id": ent_id,
            "analyst": "TRACE Forensic Unit",
            "jurisdiction": "National Technical Research Organisation (NTRO)",
        }

        try:
            gen = ForensicPDFReportGenerator(str(out_path))
            pdf_file = gen.build_report(docket, metadata=meta)
            QMessageBox.information(
                self,
                "Report Generated [OFFLINE]",
                f"12-Section PDF Lead Dossier generated successfully:\n\n{pdf_file}\n\nStrictly evidentiary and audit-ready."
            )
        except Exception as e:
            QMessageBox.critical(self, "PDF Export Error", f"Failed to generate PDF lead report:\n\n{e}")

    def _export_alerts_csv(self):
        if not self.pipeline or not self.pipeline.alerts:
            QMessageBox.warning(self, "No Data", "No alerts available to export.")
            return
        settings = get_settings()
        out_path = settings.EXPORTS_DIR / "alerts_export.csv"
        export_alerts_to_csv(self.pipeline.alerts, out_path)
        QMessageBox.information(self, "CSV Export", f"Alerts exported to:\n{out_path}")

    def _export_entities_csv(self):
        if not self.pipeline or not self.pipeline.entities:
            QMessageBox.warning(self, "No Data", "No resolved entities available to export.")
            return
        settings = get_settings()
        out_path = settings.EXPORTS_DIR / "entities_export.csv"
        export_entities_to_csv(list(self.pipeline.entities.values()), out_path)
        QMessageBox.information(self, "CSV Export", f"Entities exported to:\n{out_path}")

    def _export_docket_json(self):
        ent_id = self.entity_combo.currentText()
        if not ent_id or not self.pipeline or ent_id not in self.pipeline.dockets:
            QMessageBox.warning(self, "No Target", "Please select an entity with an active evidence docket.")
            return
        settings = get_settings()
        out_path = settings.EXPORTS_DIR / f"docket_{ent_id}.json"
        export_docket_to_json(self.pipeline.dockets[ent_id], out_path)
        QMessageBox.information(self, "JSON Export", f"Evidence docket exported to:\n{out_path}")
