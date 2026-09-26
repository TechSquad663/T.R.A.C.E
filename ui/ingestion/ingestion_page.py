"""Dataset Ingestion and validation page."""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from app.theme import THEME_COLORS
from ui.components import KPICard


class IngestionPage(QWidget):
    """File ingestion, schema mapping, and validation station."""

    run_pipeline_requested = Signal(object, object)  # (data_path_or_records, ground_truth)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header Info
        header_box = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("DATASET INGESTION & QUALITY VALIDATION")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        subtitle = QLabel("Supports offline bulk Bitcoin P2P and transaction metadata in CSV, JSON, and XML formats.")
        subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_box.addLayout(title_box)
        header_box.addStretch()

        # Import Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        self.btn_csv = QPushButton("📄 Import CSV")
        self.btn_csv.setStyleSheet(f"background-color: #1F2937; border: 1px solid #374151; color: white; padding: 8px 14px; border-radius: 6px; font-weight: 600;")
        self.btn_csv.clicked.connect(lambda: self._open_file_dialog("csv"))

        self.btn_json = QPushButton("{ } Import JSON")
        self.btn_json.setStyleSheet(f"background-color: #1F2937; border: 1px solid #374151; color: white; padding: 8px 14px; border-radius: 6px; font-weight: 600;")
        self.btn_json.clicked.connect(lambda: self._open_file_dialog("json"))

        self.btn_xml = QPushButton("📋 Import XML")
        self.btn_xml.setStyleSheet(f"background-color: #1F2937; border: 1px solid #374151; color: white; padding: 8px 14px; border-radius: 6px; font-weight: 600;")
        self.btn_xml.clicked.connect(lambda: self._open_file_dialog("xml"))

        self.btn_generate = QPushButton("⚡ Generate Demo Dataset")
        self.btn_generate.setStyleSheet(f"background-color: #059669; border: none; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 700;")
        self.btn_generate.clicked.connect(self._generate_demo)

        btn_box.addWidget(self.btn_csv)
        btn_box.addWidget(self.btn_json)
        btn_box.addWidget(self.btn_xml)
        btn_box.addWidget(self.btn_generate)

        header_box.addLayout(btn_box)
        layout.addLayout(header_box)

        # Quality Metrics Banner
        kpi_box = QHBoxLayout()
        kpi_box.setSpacing(12)
        self.card_total = KPICard("Total Records", "0", "Awaiting ingestion", THEME_COLORS["accent_blue"])
        self.card_valid = KPICard("Valid Records", "0", "Passed all checks", THEME_COLORS["accent_emerald"])
        self.card_quarantined = KPICard("Quarantined", "0", "Anomalous schema", THEME_COLORS["accent_amber"])
        self.card_duplicates = KPICard("Duplicates", "0", "Identical TXIDs", THEME_COLORS["accent_orange"])

        kpi_box.addWidget(self.card_total)
        kpi_box.addWidget(self.card_valid)
        kpi_box.addWidget(self.card_quarantined)
        kpi_box.addWidget(self.card_duplicates)
        layout.addLayout(kpi_box)

        # File Status Card
        self.status_card = QFrame()
        self.status_card.setStyleSheet(f"""
            background-color: {THEME_COLORS['bg_card']};
            border: 1px solid {THEME_COLORS['border']};
            border-radius: 6px;
            padding: 12px;
        """)
        s_layout = QHBoxLayout(self.status_card)
        self.file_info_lbl = QLabel("Active Source: None selected")
        self.file_info_lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-weight: 600;")
        s_layout.addWidget(self.file_info_lbl)
        s_layout.addStretch()

        self.btn_run = QPushButton("🚀 Run Forensic Investigation")
        self.btn_run.setStyleSheet(f"""
            QPushButton {{
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 700;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #1D4ED8; }}
            QPushButton:disabled {{ background-color: #1F2937; color: #4B5563; }}
        """)
        self.btn_run.setEnabled(False)
        self.btn_run.clicked.connect(self._run_investigation)
        s_layout.addWidget(self.btn_run)

        layout.addWidget(self.status_card)

        # Validation Preview Table
        preview_lbl = QLabel("INGESTED DATASET PREVIEW & FIELD QUALITY")
        preview_lbl.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['text_primary']}; margin-top: 6px;")
        layout.addWidget(preview_lbl)

        self.preview_table = QTableWidget(0, 7)
        self.preview_table.setHorizontalHeaderLabels([
            "TXID", "Timestamp (UTC)", "Source IP", "Inputs", "Outputs", "Total BTC", "Validation Status"
        ])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.preview_table)

        # Internal active payload
        self.active_data_source = None
        self.active_ground_truth = None

    def _open_file_dialog(self, ext: str):
        filters = {
            "csv": "CSV Files (*.csv)",
            "json": "JSON Files (*.json *.jsonl)",
            "xml": "XML Files (*.xml)",
        }
        path, _ = QFileDialog.getOpenFileName(self, f"Open {ext.upper()} Dataset", "", filters.get(ext, "All Files (*)"))
        if path:
            self.active_data_source = Path(path)
            self.active_ground_truth = None
            self.file_info_lbl.setText(f"Active File: {Path(path).name} ({Path(path).stat().st_size // 1024} KB)")
            self.btn_run.setEnabled(True)
            self._preview_loaded_file(path, ext)

    def _preview_loaded_file(self, filepath: str, fmt: str):
        p = Path(filepath)
        records = []
        if fmt == "csv":
            from ingestion.csv_loader import load_csv_data
            records, _ = load_csv_data(p, max_rows=50)
        elif fmt == "json":
            from ingestion.json_loader import load_json_data
            records, _ = load_json_data(p, max_rows=50)
        elif fmt == "xml":
            from ingestion.xml_loader import load_xml_data
            records, _ = load_xml_data(p, max_rows=50)

        self.preview_table.setRowCount(0)
        for i, r in enumerate(records):
            self.preview_table.insertRow(i)
            txid = str(r.get("txid", ""))[:16] + "..."
            self.preview_table.setItem(i, 0, QTableWidgetItem(txid))
            self.preview_table.setItem(i, 1, QTableWidgetItem(str(r.get("timestamp", ""))[:19]))
            self.preview_table.setItem(i, 2, QTableWidgetItem(str(r.get("src_ip", ""))))
            self.preview_table.setItem(i, 3, QTableWidgetItem(str(len(r.get("input_addresses", [])))))
            self.preview_table.setItem(i, 4, QTableWidgetItem(str(len(r.get("output_addresses", [])))))
            self.preview_table.setItem(i, 5, QTableWidgetItem(str(r.get("fee", "0.0"))))
            self.preview_table.setItem(i, 6, QTableWidgetItem("Ready for Validation"))

        self.card_total.set_value(str(len(records)))

    def _generate_demo(self):
        from generator.synthetic_dataset import SyntheticBitcoinTrafficGenerator
        gen = SyntheticBitcoinTrafficGenerator(seed=42)
        records, gt = gen.generate_dataset(num_transactions=1200)
        self.active_data_source = records
        self.active_ground_truth = gt
        self.file_info_lbl.setText("Active Feed: Synthetic Demo Dataset (1200 transactions, seed=42)")
        self.btn_run.setEnabled(True)

        self.preview_table.setRowCount(0)
        for i, r in enumerate(records[:50]):
            self.preview_table.insertRow(i)
            self.preview_table.setItem(i, 0, QTableWidgetItem(r["txid"][:16] + "..."))
            self.preview_table.setItem(i, 1, QTableWidgetItem(r["timestamp"][:19]))
            self.preview_table.setItem(i, 2, QTableWidgetItem(r["src_ip"]))
            self.preview_table.setItem(i, 3, QTableWidgetItem(str(len(r["input_addresses"]))))
            self.preview_table.setItem(i, 4, QTableWidgetItem(str(len(r["output_addresses"]))))
            self.preview_table.setItem(i, 5, QTableWidgetItem(f"{sum(r['output_amounts']):.4f}"))
            self.preview_table.setItem(i, 6, QTableWidgetItem("Validated / Ground Truth Available"))

        self.card_total.set_value(str(len(records)))
        self.card_valid.set_value(str(len(records)))

    def _run_investigation(self):
        if self.active_data_source is not None:
            self.run_pipeline_requested.emit(self.active_data_source, self.active_ground_truth)

    def update_quality_report(self, report):
        if report:
            self.card_total.set_value(str(report.total_records))
            self.card_valid.set_value(str(report.valid_records))
            self.card_quarantined.set_value(str(report.quarantined_records))
            self.card_duplicates.set_value(str(report.duplicate_records))
