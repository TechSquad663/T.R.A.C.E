"""Main Application Window for TRACE Forensic Intelligence Workstation."""
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QProgressDialog, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal

from config.settings import get_settings
from pipeline.investigation_pipeline import InvestigationPipeline
from generator.synthetic_dataset import SyntheticBitcoinTrafficGenerator
from app.theme import THEME_COLORS, theme_manager

from .sidebar import Sidebar
from .header import Header
from .status_bar import StatusBar

from .overview.overview_page import OverviewPage
from .ingestion.ingestion_page import IngestionPage
from .transactions.transaction_page import TransactionPage
from .entities.entity_page import EntityPage
from .graph.graph_page import GraphPage
from .anomalies.anomaly_page import AnomalyPage
from .alerts.alerts_page import AlertsPage
from .investigations.investigations_page import InvestigationsPage
from .evidence.evidence_page import EvidencePage
from .evaluation.evaluation_page import EvaluationPage
from .reports.reports_page import ReportsPage
from .settings.settings_page import SettingsPage

logger = logging.getLogger("TRACE.MainWindow")


class PipelineWorkerThread(QThread):
    """Executes heavy investigation pipeline asynchronously so GUI never freezes."""

    progress_signal = Signal(int, int, str)
    finished_signal = Signal(dict)
    error_signal = Signal(str)

    def __init__(self, pipeline: InvestigationPipeline, data_source, ground_truth=None):
        super().__init__()
        self.pipeline = pipeline
        self.data_source = data_source
        self.ground_truth = ground_truth

    def run(self):
        try:
            def callback(step, total, msg):
                self.progress_signal.emit(step, total, msg)

            res = self.pipeline.run_investigation(
                self.data_source,
                ground_truth=self.ground_truth,
                progress_callback=callback,
            )
            self.finished_signal.emit(res)
        except Exception as e:
            logger.error(f"Investigation pipeline error: {e}", exc_info=True)
            self.error_signal.emit(str(e))


class MainWindow(QMainWindow):
    """TRACE Native Forensic Desktop Application Window."""

    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.setWindowTitle(self.settings.WINDOW_TITLE)
        self.resize(self.settings.DEFAULT_WINDOW_WIDTH, self.settings.DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(1100, 700)

        # Core state
        self.pipeline = InvestigationPipeline()
        self.worker_thread: Optional[PipelineWorkerThread] = None

        # Build Central Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._on_page_changed)
        main_layout.addWidget(self.sidebar)

        # 2. Right Main Workstation Area
        work_area = QWidget()
        work_layout = QVBoxLayout(work_area)
        work_layout.setContentsMargins(0, 0, 0, 0)
        work_layout.setSpacing(0)

        # Top Header
        self.header = Header()
        self.header.run_demo_requested.connect(self.run_demo_investigation)
        self.header.import_dataset_requested.connect(lambda: self.sidebar.set_active_page(1))
        work_layout.addWidget(self.header)

        # Page Stack
        self.stack = QStackedWidget()
        self._init_pages()
        work_layout.addWidget(self.stack, 1)

        main_layout.addWidget(work_area, 1)

        # Status Bar
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

    def _init_pages(self):
        # Page 0: Overview
        self.page_overview = OverviewPage(
            on_generate_demo=self.run_demo_investigation,
            on_import_dataset=lambda: self.sidebar.set_active_page(1),
        )
        self.stack.addWidget(self.page_overview)

        # Page 1: Ingestion
        self.page_ingestion = IngestionPage()
        self.page_ingestion.run_pipeline_requested.connect(self._start_pipeline_execution)
        self.stack.addWidget(self.page_ingestion)

        # Page 2: Transactions
        self.page_transactions = TransactionPage()
        self.stack.addWidget(self.page_transactions)

        # Page 3: Entities
        self.page_entities = EntityPage()
        self.stack.addWidget(self.page_entities)

        # Page 4: Link Analysis
        self.page_graph = GraphPage()
        self.stack.addWidget(self.page_graph)

        # Page 5: Anomalies
        self.page_anomalies = AnomalyPage()
        self.stack.addWidget(self.page_anomalies)

        # Page 6: Alerts
        self.page_alerts = AlertsPage()
        self.stack.addWidget(self.page_alerts)

        # Page 7: Investigations
        self.page_investigations = InvestigationsPage()
        self.stack.addWidget(self.page_investigations)

        # Page 8: Evidence
        self.page_evidence = EvidencePage()
        self.stack.addWidget(self.page_evidence)

        # Page 9: Evaluation
        self.page_evaluation = EvaluationPage()
        self.stack.addWidget(self.page_evaluation)

        # Page 10: Reports
        self.page_reports = ReportsPage()
        self.stack.addWidget(self.page_reports)

        # Page 11: Settings
        self.page_settings = SettingsPage()
        self.stack.addWidget(self.page_settings)

    PAGE_NAMES = [
        "Command Center",
        "Dataset Ingestion",
        "Transactions",
        "Entities & Wallets",
        "Link Analysis",
        "Behavioral Anomalies",
        "Ranked Alerts",
        "Investigations",
        "Evidence Chain",
        "Model Evaluation",
        "Reports & Exports",
        "System & Settings",
    ]

    def _on_page_changed(self, page_index: int):
        self.stack.setCurrentIndex(page_index)
        if 0 <= page_index < len(self.PAGE_NAMES):
            self.header.set_page_title(self.PAGE_NAMES[page_index])

    def run_demo_investigation(self):
        """One-click deterministic demo investigation."""
        self.status_bar.set_status("Generating realistic demo dataset (seed=42)...")
        gen = SyntheticBitcoinTrafficGenerator(seed=42)
        records, gt = gen.generate_dataset(num_transactions=1200)
        self._start_pipeline_execution(records, ground_truth=gt, is_demo=True)

    def _start_pipeline_execution(self, data_source, ground_truth=None, is_demo=False):
        """Launch background worker thread for investigation."""
        # Progress Dialog
        self.progress_dialog = QProgressDialog("Initializing forensic analysis pipeline...", "Cancel", 0, 14, self)
        self.progress_dialog.setWindowTitle("TRACE Analysis Pipeline [100% OFFLINE]")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setStyleSheet(f"QProgressDialog {{ background-color: {THEME_COLORS['bg_dark']}; color: {THEME_COLORS['text_primary']}; }}")

        # Worker Thread
        self.worker_thread = PipelineWorkerThread(self.pipeline, data_source, ground_truth)
        self.worker_thread.progress_signal.connect(self._on_pipeline_progress)
        self.worker_thread.finished_signal.connect(lambda res: self._on_pipeline_finished(res, is_demo))
        self.worker_thread.error_signal.connect(self._on_pipeline_error)
        self.worker_thread.start()

    def _on_pipeline_progress(self, step: int, total: int, msg: str):
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.setValue(step)
            self.progress_dialog.setLabelText(f"Stage {step}/{total}: {msg}")
        self.status_bar.set_status(f"Stage [{step}/{total}]: {msg}")

    def _on_pipeline_finished(self, results: dict, is_demo: bool):
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        # Update header
        name = "Synthetic Demo Dataset (seed=42)" if is_demo else "Imported Dataset"
        self.header.set_dataset_info(name, results["total_records"])

        # Broadcast state updates to all sub-pages
        self.page_overview.update_data(self.pipeline)
        self.page_ingestion.update_quality_report(self.pipeline.quality_report)
        self.page_transactions.update_data(self.pipeline)
        self.page_entities.update_data(self.pipeline)
        self.page_graph.update_data(self.pipeline)
        self.page_anomalies.update_data(self.pipeline)
        self.page_alerts.update_data(self.pipeline)
        self.page_investigations.update_data(self.pipeline)
        self.page_evidence.update_data(self.pipeline)
        self.page_evaluation.update_data(self.pipeline)
        self.page_reports.update_data(self.pipeline)

        self.status_bar.set_status(
            f"Investigation Complete: {results['total_records']} transactions • "
            f"{results['total_entities']} entities • {results['high_priority_leads']} high-priority leads"
        )

        # Switch to overview page
        self.sidebar.set_active_page(0)
        self.stack.setCurrentIndex(0)

        QMessageBox.information(
            self,
            "Investigation Completed",
            f"Forensic Investigation Pipeline completed successfully!\n\n"
            f"• Valid Records Processed: {results['total_records']}\n"
            f"• Resolved Entities: {results['total_entities']}\n"
            f"• Ranked Alerts Generated: {results['total_alerts']}\n"
            f"• High-Priority Leads: {results['high_priority_leads']}\n\n"
            f"All link analysis graphs, SHAP attributions, and evidence dossiers are ready for review."
        )

    def _on_pipeline_error(self, err_msg: str):
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()
        self.status_bar.set_status("Investigation failed.")
        QMessageBox.critical(self, "Pipeline Error", f"An error occurred during dataset analysis:\n\n{err_msg}")
