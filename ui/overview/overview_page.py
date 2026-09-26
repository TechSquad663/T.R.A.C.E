"""Overview dashboard page displaying dataset-derived KPIs and risk distribution."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
from ui.components import KPICard, RiskBadge, EmptyStateWidget


class OverviewPage(QWidget):
    """Primary intelligence overview dashboard presenting analysis summaries."""

    def __init__(self, on_generate_demo=None, on_import_dataset=None):
        super().__init__()
        self.on_generate_demo = on_generate_demo
        self.on_import_dataset = on_import_dataset

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Empty state container
        self.empty_widget = EmptyStateWidget(on_generate_demo, on_import_dataset)
        main_layout.addWidget(self.empty_widget)

        # Content container
        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setContentsMargins(24, 20, 24, 20)
        self.layout.setSpacing(20)

        # Header Info Banner
        self.banner = QFrame()
        b_layout = QVBoxLayout(self.banner)
        b_layout.setContentsMargins(8, 4, 8, 4)
        b_layout.setSpacing(2)

        self.banner_title = QLabel("ANALYTICAL INTELLIGENCE OVERVIEW (OFFLINE DATASET)")
        self.banner_sub = QLabel("Metrics derived exclusively from ingested metadata. Reflects behavioral deviations, graph centrality, and ML indicators.")
        b_layout.addWidget(self.banner_title)
        b_layout.addWidget(self.banner_sub)
        self.layout.addWidget(self.banner)

        # KPI Cards Grid
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(12)

        self.kpi_records = KPICard("Validated Records", "0", "Ingested from offline feed", "#38BDF8")
        self.kpi_wallets = KPICard("Resolved Wallets", "0", "Unique on-chain addresses", "#A855F7")
        self.kpi_ips = KPICard("Observed IPs", "0", "P2P broadcast nodes", "#06B6D4")
        self.kpi_entities = KPICard("Behavioral Entities", "0", "Resolved via CIO heuristic", "#10B981")
        self.kpi_anomalies = KPICard("Statistical Anomalies", "0", "Isolation Forest tail", "#F59E0B")
        self.kpi_critical = KPICard("High-Priority Leads", "0", "Risk Score >= 65", "#EF4444")

        kpi_grid.addWidget(self.kpi_records, 0, 0)
        kpi_grid.addWidget(self.kpi_wallets, 0, 1)
        kpi_grid.addWidget(self.kpi_ips, 0, 2)
        kpi_grid.addWidget(self.kpi_entities, 1, 0)
        kpi_grid.addWidget(self.kpi_anomalies, 1, 1)
        kpi_grid.addWidget(self.kpi_critical, 1, 2)

        self.layout.addLayout(kpi_grid)

        # Two Column Section: Top Leads Table & Summary Metrics
        sec_layout = QHBoxLayout()
        sec_layout.setSpacing(16)

        # Left: Top Leads Table
        self.tbl_frame = QFrame()
        tbl_layout = QVBoxLayout(self.tbl_frame)
        tbl_layout.setContentsMargins(8, 8, 8, 8)
        tbl_layout.setSpacing(8)

        self.tbl_title = QLabel("TOP RANKED INVESTIGATIVE LEADS")
        tbl_layout.addWidget(self.tbl_title)

        self.leads_table = QTableWidget(0, 5)
        self.leads_table.setHorizontalHeaderLabels(["Priority", "Entity ID", "Risk", "Pattern", "Confidence"])
        self.leads_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.leads_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.leads_table.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl_layout.addWidget(self.leads_table)

        sec_layout.addWidget(self.tbl_frame, 2)

        # Right: Geo & Graph Summary Card
        self.info_frame = QFrame()
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(12, 12, 12, 12)
        info_layout.setSpacing(10)

        self.info_title = QLabel("TOPOLOGICAL & NETWORK SUMMARY")
        info_layout.addWidget(self.info_title)

        self.lbl_graph_summary = QLabel("Graph Topology: 0 nodes, 0 edges")
        info_layout.addWidget(self.lbl_graph_summary)

        self.lbl_geo_summary = QLabel("Jurisdiction Diversity: 0 countries observed")
        info_layout.addWidget(self.lbl_geo_summary)

        self.lbl_model_backend = QLabel("Supervised Engine: XGBoost (Tree Ensemble)")
        info_layout.addWidget(self.lbl_model_backend)

        self.lbl_cio_summary = QLabel("Common-Input Entities: 0 multi-wallet clusters")
        info_layout.addWidget(self.lbl_cio_summary)

        info_layout.addStretch()
        sec_layout.addWidget(self.info_frame, 1)

        self.layout.addLayout(sec_layout)

        self.content_scroll.setWidget(content_widget)
        main_layout.addWidget(self.content_scroll)
        self.content_scroll.hide()

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update frames, labels, and table styling when theme changes."""
        self.banner.setStyleSheet(f"""
            background-color: {THEME_COLORS['bg_card']};
            border: 1px solid {THEME_COLORS['border']};
            border-left: 4px solid {THEME_COLORS['accent_blue']};
            border-radius: 6px;
            padding: 12px;
        """)
        self.banner_title.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.banner_sub.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")

        self.tbl_frame.setStyleSheet(f"""
            background-color: {THEME_COLORS['bg_card']};
            border: 1px solid {THEME_COLORS['border']};
            border-radius: 8px;
            padding: 14px;
        """)
        self.tbl_title.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['text_primary']};")

        self.info_frame.setStyleSheet(f"""
            background-color: {THEME_COLORS['bg_card']};
            border: 1px solid {THEME_COLORS['border']};
            border-radius: 8px;
            padding: 14px;
        """)
        self.info_title.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['text_primary']};")

        self.lbl_graph_summary.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px;")
        self.lbl_geo_summary.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px;")
        self.lbl_model_backend.setStyleSheet(f"color: {THEME_COLORS['accent_blue']}; font-size: 12px; font-weight: 600;")
        self.lbl_cio_summary.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px;")

    def update_data(self, pipeline):
        """Populate overview dashboard from executed pipeline state."""
        if not pipeline or not pipeline.records:
            self.empty_widget.show()
            self.content_scroll.hide()
            return

        self.empty_widget.hide()
        self.content_scroll.show()

        # Update KPIs
        self.kpi_records.set_value(str(len(pipeline.records)))
        wallets_cnt = sum(len(e.addresses) for e in pipeline.entities.values())
        self.kpi_wallets.set_value(str(wallets_cnt))

        unique_ips = len(set(r.src_ip for r in pipeline.records if r.src_ip))
        self.kpi_ips.set_value(str(unique_ips))

        self.kpi_entities.set_value(str(len(pipeline.entities)))

        anomalies_cnt = sum(1 for e in pipeline.entities.values() if e.anomaly_score >= 0.70)
        self.kpi_anomalies.set_value(str(anomalies_cnt))

        crit_cnt = sum(1 for a in pipeline.alerts if a.priority.value in ["Critical", "High"])
        self.kpi_critical.set_value(str(crit_cnt))

        # Update Leads Table
        self.leads_table.setRowCount(0)
        for row_idx, a in enumerate(pipeline.alerts[:10]):
            self.leads_table.insertRow(row_idx)
            self.leads_table.setItem(row_idx, 0, QTableWidgetItem(a.priority.value))
            self.leads_table.setItem(row_idx, 1, QTableWidgetItem(a.entity_id))
            self.leads_table.setItem(row_idx, 2, QTableWidgetItem(f"{a.risk_score}/100"))
            self.leads_table.setItem(row_idx, 3, QTableWidgetItem(a.pattern))
            self.leads_table.setItem(row_idx, 4, QTableWidgetItem(f"{int(a.confidence * 100)}%"))

        # Topology summary
        if pipeline.graph:
            self.lbl_graph_summary.setText(f"Graph Topology: {pipeline.graph.number_of_nodes()} nodes, {pipeline.graph.number_of_edges()} edges")
        countries = set(r.geo_country for r in pipeline.records if r.geo_country != "Unknown")
        self.lbl_geo_summary.setText(f"Jurisdiction Diversity: {len(countries)} countries observed")

        cio_clusters = sum(1 for e in pipeline.entities.values() if len(e.addresses) > 1)
        self.lbl_cio_summary.setText(f"Common-Input Entities: {cio_clusters} multi-wallet heuristic clusters")
