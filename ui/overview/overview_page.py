"""Overview dashboard page displaying dataset-derived KPIs, risk distribution, and forensic charts."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
from ui.components import KPICard, RiskBadge, EmptyStateWidget, setup_table_headers
from ui.charts import ForensicCard, DonutChartWidget, ActivityLineChartWidget, HorizontalBarChartWidget
from ui.alerts.alert_details import AlertDetailsDialog


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
        self.layout.setContentsMargins(20, 16, 20, 16)
        self.layout.setSpacing(16)

        # Header Info Banner
        self.banner = QFrame()
        b_layout = QVBoxLayout(self.banner)
        b_layout.setContentsMargins(10, 8, 10, 8)
        b_layout.setSpacing(2)

        self.banner_title = QLabel("ANALYTICAL INTELLIGENCE OVERVIEW (OFFLINE DATASET)")
        self.banner_sub = QLabel("Metrics derived exclusively from ingested metadata. Reflects behavioral deviations, graph centrality, and ML indicators.")
        b_layout.addWidget(self.banner_title)
        b_layout.addWidget(self.banner_sub)
        self.layout.addWidget(self.banner)

        # KPI Cards Grid (6 cards)
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

        # Forensic Charts Row: Activity Timeline | Risk Tier Donut | Alert Priority
        charts_row = QHBoxLayout()
        charts_row.setSpacing(14)

        # 1. Activity Line Chart Card
        self.activity_card = ForensicCard("TRANSACTION TRAFFIC TIMELINE", "Temporal observation count over time")
        self.activity_chart = ActivityLineChartWidget()
        self.activity_card.add_widget(self.activity_chart)
        charts_row.addWidget(self.activity_card, 2)

        # 2. Risk Donut Card
        self.risk_card = ForensicCard("RISK SCORE DISTRIBUTION", "Entity risk tier segmentation (0-100)")
        self.risk_donut = DonutChartWidget()
        self.risk_card.add_widget(self.risk_donut)
        charts_row.addWidget(self.risk_card, 1)

        # 3. Priority Bar Card
        self.priority_card = ForensicCard("INVESTIGATIVE PRIORITIES", "Lead severity breakdown")
        self.priority_chart = HorizontalBarChartWidget()
        self.priority_card.add_widget(self.priority_chart)
        charts_row.addWidget(self.priority_card, 1)

        self.layout.addLayout(charts_row)

        # Lower Section: Top Leads Table & Behavioral Patterns / Summary
        sec_layout = QHBoxLayout()
        sec_layout.setSpacing(14)

        # Left: Top Leads Table
        self.tbl_frame = QFrame()
        tbl_layout = QVBoxLayout(self.tbl_frame)
        tbl_layout.setContentsMargins(12, 10, 12, 10)
        tbl_layout.setSpacing(8)

        self.tbl_title = QLabel("TOP RANKED INVESTIGATIVE LEADS")
        tbl_layout.addWidget(self.tbl_title)

        self.leads_table = QTableWidget(0, 5)
        setup_table_headers(self.leads_table)
        self.leads_table.setHorizontalHeaderLabels(["Priority", "Entity ID", "Risk", "Pattern", "Confidence"])
        header = self.leads_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        self.leads_table.setColumnWidth(1, 185)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.leads_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.leads_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.leads_table.setMinimumHeight(220)
        self.leads_table.doubleClicked.connect(self._open_lead_details)
        tbl_layout.addWidget(self.leads_table)

        sec_layout.addWidget(self.tbl_frame, 2)

        # Right: Pattern Breakdown & Topological Summary
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)

        self.pattern_card = ForensicCard("DETECTED BEHAVIORAL PATTERNS", "Top anomalous behavior heuristics")
        self.pattern_chart = HorizontalBarChartWidget()
        self.pattern_card.add_widget(self.pattern_chart)
        right_panel.addWidget(self.pattern_card)

        # Geo & Graph Summary Card
        self.info_frame = QFrame()
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(12, 10, 12, 10)
        info_layout.setSpacing(8)

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

        right_panel.addWidget(self.info_frame)
        sec_layout.addLayout(right_panel, 1)

        self.layout.addLayout(sec_layout, 1)

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
            padding: 10px;
        """)
        self.banner_title.setStyleSheet(f"background: transparent; font-size: 13px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.banner_sub.setStyleSheet(f"background: transparent; font-size: 11px; color: {THEME_COLORS['text_secondary']};")

        self.tbl_frame.setStyleSheet(f"""
            background-color: {THEME_COLORS['bg_card']};
            border: 1px solid {THEME_COLORS['border']};
            border-radius: 8px;
        """)
        self.tbl_title.setStyleSheet(f"background: transparent; font-size: 11px; font-weight: 700; color: {THEME_COLORS['text_primary']}; letter-spacing: 0.5px;")

        self.info_frame.setStyleSheet(f"""
            background-color: {THEME_COLORS['bg_card']};
            border: 1px solid {THEME_COLORS['border']};
            border-radius: 8px;
        """)
        self.info_title.setStyleSheet(f"background: transparent; font-size: 11px; font-weight: 700; color: {THEME_COLORS['text_primary']}; letter-spacing: 0.5px;")

        self.lbl_graph_summary.setStyleSheet(f"background: transparent; color: {THEME_COLORS['text_secondary']}; font-size: 11px;")
        self.lbl_geo_summary.setStyleSheet(f"background: transparent; color: {THEME_COLORS['text_secondary']}; font-size: 11px;")
        self.lbl_model_backend.setStyleSheet(f"background: transparent; color: {THEME_COLORS['accent_blue']}; font-size: 11px; font-weight: 600;")
        self.lbl_cio_summary.setStyleSheet(f"background: transparent; color: {THEME_COLORS['text_secondary']}; font-size: 11px;")

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

        # 1. Update Activity Timeline
        timestamps = []
        for r in pipeline.records:
            if r.timestamp:
                ts_str = str(r.timestamp).replace("Z", "").replace(" ", "T")
                timestamps.append(ts_str)

        if timestamps:
            timestamps.sort()
            n_buckets = min(8, len(timestamps))
            if n_buckets > 1:
                bucket_size = len(timestamps) / n_buckets
                bucket_data = []
                for b in range(n_buckets):
                    start_idx = int(b * bucket_size)
                    end_idx = int(min(len(timestamps), (b + 1) * bucket_size))
                    t_label = timestamps[start_idx].split("T")[-1][:5] if "T" in timestamps[start_idx] else timestamps[start_idx][-5:]
                    count = end_idx - start_idx
                    bucket_data.append((t_label, float(count)))
                self.activity_chart.set_data(bucket_data)
            else:
                self.activity_chart.set_data([(timestamps[0][:10], float(len(timestamps)))])
        else:
            self.activity_chart.set_data([])

        # 2. Update Risk Donut Distribution
        crit_risk = sum(1 for e in pipeline.entities.values() if e.risk_score >= 75)
        high_risk = sum(1 for e in pipeline.entities.values() if 50 <= e.risk_score < 75)
        med_risk = sum(1 for e in pipeline.entities.values() if 25 <= e.risk_score < 50)
        low_risk = sum(1 for e in pipeline.entities.values() if e.risk_score < 25)
        self.risk_donut.set_data([
            ("Critical", crit_risk, THEME_COLORS["accent_red"]),
            ("High", high_risk, THEME_COLORS["accent_orange"]),
            ("Medium", med_risk, THEME_COLORS["accent_amber"]),
            ("Low", low_risk, THEME_COLORS["accent_emerald"]),
        ])

        # 3. Update Alert Priority Distribution
        p_crit = sum(1 for a in pipeline.alerts if a.priority.value == "Critical")
        p_high = sum(1 for a in pipeline.alerts if a.priority.value == "High")
        p_med = sum(1 for a in pipeline.alerts if a.priority.value == "Medium")
        p_low = sum(1 for a in pipeline.alerts if a.priority.value == "Low")
        self.priority_chart.set_data([
            ("Critical", p_crit, THEME_COLORS["accent_red"]),
            ("High", p_high, THEME_COLORS["accent_orange"]),
            ("Medium", p_med, THEME_COLORS["accent_amber"]),
            ("Low", p_low, THEME_COLORS["accent_emerald"]),
        ])

        # 4. Update Pattern Breakdown
        pattern_counts = {}
        for a in pipeline.alerts:
            p = a.pattern or "Unspecified"
            pattern_counts[p] = pattern_counts.get(p, 0) + 1
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:4]
        colors = [THEME_COLORS["accent_red"], THEME_COLORS["accent_orange"], THEME_COLORS["accent_purple"], THEME_COLORS["accent_blue"]]
        pattern_data = [(name, count, colors[i % len(colors)]) for i, (name, count) in enumerate(sorted_patterns)]
        self.pattern_chart.set_data(pattern_data)

        # Update Leads Table
        self.leads_table.setRowCount(0)
        for row_idx, a in enumerate(pipeline.alerts[:10]):
            self.leads_table.insertRow(row_idx)
            self.leads_table.setItem(row_idx, 0, QTableWidgetItem(a.priority.value))
            self.leads_table.setItem(row_idx, 1, QTableWidgetItem(a.entity_id))
            self.leads_table.setItem(row_idx, 2, QTableWidgetItem(f"{a.risk_score:.1f}/100"))
            
            pat_item = QTableWidgetItem(a.pattern)
            if a.reasons:
                pat_item.setToolTip("Forensic Rationale:\n• " + "\n• ".join(a.reasons))
            self.leads_table.setItem(row_idx, 3, pat_item)
            
            self.leads_table.setItem(row_idx, 4, QTableWidgetItem(f"{int(a.confidence * 100)}%"))

        # Topology summary
        if pipeline.graph:
            self.lbl_graph_summary.setText(f"Graph Topology: {pipeline.graph.number_of_nodes()} nodes, {pipeline.graph.number_of_edges()} edges")
        countries = set(r.geo_country for r in pipeline.records if r.geo_country != "Unknown")
        self.lbl_geo_summary.setText(f"Jurisdiction Diversity: {len(countries)} countries observed")

        cio_clusters = sum(1 for e in pipeline.entities.values() if len(e.addresses) > 1)
        self.lbl_cio_summary.setText(f"Common-Input Entities: {cio_clusters} multi-wallet heuristic clusters")
        self.pipeline = pipeline

    def _open_lead_details(self, index):
        row = index.row()
        if hasattr(self, "pipeline") and self.pipeline and row < len(self.pipeline.alerts):
            alert = self.pipeline.alerts[row]
            dialog = AlertDetailsDialog(alert, parent=self)
            dialog.exec()
