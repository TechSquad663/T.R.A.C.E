"""Reports and Exports page."""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QFrame, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS
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
        title = QLabel("FORENSIC REPORT GENERATION & DATA EXPORTS")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        subtitle = QLabel("Generate audit-ready 12-section PDF lead reports, evidence dossiers, and tabular CSV extracts.")
        subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        # PDF Report Section Card
        pdf_card = QFrame()
        pdf_card.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 8px; padding: 16px;")
        pc_layout = QVBoxLayout(pdf_card)
        pc_layout.setSpacing(12)

        pc_title = QLabel("📄 TRACE INVESTIGATIVE LEAD REPORT (PDF)")
        pc_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        pc_layout.addWidget(pc_title)

        pc_desc = QLabel(
            "Compiles a comprehensive 12-section offline PDF dossier including executive summary, "
            "risk fusion indicators, SHAP attributions, network relay endpoints, multi-hop evidence chains, "
            "and statutory disclaimers."
        )
        pc_desc.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px;")
        pc_layout.addWidget(pc_desc)

        ent_select_box = QHBoxLayout()
        ent_select_box.addWidget(QLabel("Select Target Lead:"))
        self.entity_combo = QComboBox()
        self.entity_combo.setStyleSheet("min-width: 280px;")
        ent_select_box.addWidget(self.entity_combo)
        ent_select_box.addStretch()

        self.btn_gen_pdf = QPushButton("📑 Generate Official PDF Lead Report")
        self.btn_gen_pdf.setStyleSheet("background-color: #2563EB; color: white; padding: 8px 18px; border-radius: 6px; font-weight: 700;")
        self.btn_gen_pdf.clicked.connect(self._generate_pdf)
        ent_select_box.addWidget(self.btn_gen_pdf)

        pc_layout.addLayout(ent_select_box)
        layout.addWidget(pdf_card)

        # Tabular Data Exports Card
        exp_card = QFrame()
        exp_card.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 8px; padding: 16px;")
        ec_layout = QVBoxLayout(exp_card)
        ec_layout.setSpacing(12)

        ec_title = QLabel("📊 TABULAR & EVIDENCE EXPORTS (CSV / JSON)")
        ec_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {THEME_COLORS['accent_emerald']};")
        ec_layout.addWidget(ec_title)

        ec_desc = QLabel("Export structured alerts, resolved entities, and raw evidence dockets for external offline analytical tools.")
        ec_desc.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px;")
        ec_layout.addWidget(ec_desc)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_exp_alerts = QPushButton("📥 Export Alerts (CSV)")
        self.btn_exp_alerts.setStyleSheet("background-color: #1F2937; border: 1px solid #374151; color: white; padding: 8px 14px; border-radius: 6px; font-weight: 600;")
        self.btn_exp_alerts.clicked.connect(self._export_alerts_csv)
        btn_row.addWidget(self.btn_exp_alerts)

        self.btn_exp_entities = QPushButton("📥 Export Entities (CSV)")
        self.btn_exp_entities.setStyleSheet("background-color: #1F2937; border: 1px solid #374151; color: white; padding: 8px 14px; border-radius: 6px; font-weight: 600;")
        self.btn_exp_entities.clicked.connect(self._export_entities_csv)
        btn_row.addWidget(self.btn_exp_entities)

        self.btn_exp_json = QPushButton("📥 Export Evidence Docket (JSON)")
        self.btn_exp_json.setStyleSheet("background-color: #1F2937; border: 1px solid #374151; color: white; padding: 8px 14px; border-radius: 6px; font-weight: 600;")
        self.btn_exp_json.clicked.connect(self._export_docket_json)
        btn_row.addWidget(self.btn_exp_json)

        btn_row.addStretch()
        ec_layout.addLayout(btn_row)
        layout.addWidget(exp_card)

        layout.addStretch()

        self.pipeline = None

    def update_data(self, pipeline):
        self.pipeline = pipeline
        if not pipeline or not pipeline.dockets:
            return
        self.entity_combo.clear()
        for ent_id in pipeline.entities.keys():
            self.entity_combo.addItem(ent_id)

    def _generate_pdf(self):
        if not self.pipeline or not self.pipeline.dockets:
            QMessageBox.warning(self, "No Data", "Please load a dataset and run investigation first.")
            return

        ent_id = self.entity_combo.currentText()
        if not ent_id or ent_id not in self.pipeline.dockets:
            return

        docket = self.pipeline.dockets[ent_id]
        out_dir = get_settings().EXPORTS_DIR
        out_file = out_dir / f"TRACE_Lead_Report_{ent_id[:16]}.pdf"

        gen = ForensicPDFReportGenerator()
        gen.generate_report(docket, out_file, {"filename": "TRACE Offline Investigation Feed"})

        QMessageBox.information(
            self,
            "Report Generated",
            f"Official TRACE Lead Report PDF successfully compiled offline:\n\n{out_file}"
        )

    def _export_alerts_csv(self):
        if not self.pipeline or not self.pipeline.alerts:
            QMessageBox.warning(self, "No Data", "No alerts to export.")
            return
        out_file = get_settings().EXPORTS_DIR / "TRACE_Ranked_Alerts.csv"
        export_alerts_to_csv(self.pipeline.alerts, out_file)
        QMessageBox.information(self, "Export Complete", f"Ranked alerts exported to:\n{out_file}")

    def _export_entities_csv(self):
        if not self.pipeline or not self.pipeline.entities:
            QMessageBox.warning(self, "No Data", "No entities to export.")
            return
        out_file = get_settings().EXPORTS_DIR / "TRACE_Resolved_Entities.csv"
        export_entities_to_csv(list(self.pipeline.entities.values()), out_file)
        QMessageBox.information(self, "Export Complete", f"Entities exported to:\n{out_file}")

    def _export_docket_json(self):
        if not self.pipeline or not self.pipeline.dockets:
            QMessageBox.warning(self, "No Data", "No evidence dockets to export.")
            return
        ent_id = self.entity_combo.currentText()
        if not ent_id or ent_id not in self.pipeline.dockets:
            return
        docket = self.pipeline.dockets[ent_id]
        out_file = get_settings().EXPORTS_DIR / f"TRACE_Evidence_Docket_{ent_id[:16]}.json"
        export_docket_to_json(docket, out_file)
        QMessageBox.information(self, "Export Complete", f"Evidence docket exported to:\n{out_file}")
